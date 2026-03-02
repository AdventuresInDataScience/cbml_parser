from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Optional

from cbml_parser.constants import (
    PRESET_LAYOUTS,
    HEADER_FIELDS,
    BUBBLE_TYPES,
    VALID_CAPTION_POSITIONS,
)
from cbml_parser.exceptions import CBMLParseError, CBMLValidationError
from cbml_parser.models import (
    Caption,
    Comic,
    CustomGrid,
    DialogueLine,
    Page,
    Panel,
    PresetLayout,
    Slot,
)
from cbml_parser.validator import ValidationResult, validate_comic


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_RE_TITLE = re.compile(r'^##\s+(.+)$')
_RE_HEADER_FIELD = re.compile(r'^(\w+):\s*(.+)$')
_RE_PAGE_PRESET = re.compile(r'^PAGE\s+preset:(\S+)$')
_RE_PAGE_GRID = re.compile(r'^PAGE\s+grid:(\d+)x(\d+)$')
_RE_SLOT = re.compile(r'^([A-Z][A-Z0-9]*):\s*\[(.+?),\s*(.+?)\]$')
_RE_PANEL = re.compile(r'^PANEL\s+([A-Z][A-Z0-9]*)$')
_RE_RANGE = re.compile(r'^(\d+)(?:-(\d+))?$')
_RE_CAPTION_BLOCK = re.compile(r'^\[caption(.*?)\]\s*(.+)$')
_RE_CAPTION_ATTR = re.compile(r'(\w+):(\S+)')
_RE_DIALOGUE = re.compile(r'^([A-Z][A-Z0-9_]*):\s*(.+)$')
_RE_HEX = re.compile(r'^#[0-9a-fA-F]{6}$')


def _parse_range(s: str, line_number: int, raw: str) -> tuple[int, int]:
    """Parse '3' or '1-3' into an inclusive (start, end) int tuple."""
    m = _RE_RANGE.match(s.strip())
    if not m:
        raise CBMLParseError(f"Invalid range expression: {s!r}", line_number, raw)
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    if start < 1 or end < start:
        raise CBMLParseError(
            f"Range {s!r} is invalid — start must be ≥ 1 and end must be ≥ start",
            line_number, raw,
        )
    return start, end


def _parse_caption(content: str, attrs_str: str, line_number: int, raw: str) -> Caption:
    """Parse a caption line into a Caption dataclass."""
    bg = "#000000"
    color = "#ffffff"
    pos = "top-left"
    warnings: list[str] = []

    for m in _RE_CAPTION_ATTR.finditer(attrs_str):
        key, value = m.group(1), m.group(2)
        if key == "bg":
            if not _RE_HEX.match(value):
                raise CBMLParseError(
                    f"Caption 'bg' attribute has invalid hex colour: {value!r}",
                    line_number, raw,
                )
            bg = value
        elif key == "color":
            if not _RE_HEX.match(value):
                raise CBMLParseError(
                    f"Caption 'color' attribute has invalid hex colour: {value!r}",
                    line_number, raw,
                )
            color = value
        elif key == "pos":
            if value not in VALID_CAPTION_POSITIONS:
                raise CBMLParseError(
                    f"Caption 'pos' value {value!r} is not valid. "
                    f"Must be one of: {', '.join(sorted(VALID_CAPTION_POSITIONS))}",
                    line_number, raw,
                )
            pos = value
        # Unknown attributes are silently ignored at parse time;
        # the validator will warn about them if needed.

    return Caption(text=content.strip(), bg=bg, color=color, pos=pos)


def _parse_dialogue(match: re.Match, line_number: int, raw: str) -> Optional[DialogueLine]:
    """
    Parse a dialogue line of the form:
      NAME: "text"
      NAME: ~text~
      NAME: !"text"!
      NAME: ?"text"?
    Returns None if the line doesn't match any known bubble format.
    """
    character = match.group(1)
    remainder = match.group(2).strip()

    if not remainder:
        return None

    first_char = remainder[0]

    if first_char == '"' and remainder.endswith('"') and len(remainder) >= 2:
        return DialogueLine(character=character, text=remainder[1:-1], bubble_type="speech")

    if first_char == '~' and remainder.endswith('~') and len(remainder) >= 2:
        return DialogueLine(character=character, text=remainder[1:-1], bubble_type="thought")

    if first_char == '!' and remainder.endswith('!') and len(remainder) >= 2:
        inner = remainder[1:-1]
        if inner.startswith('"') and inner.endswith('"'):
            inner = inner[1:-1]
        return DialogueLine(character=character, text=inner, bubble_type="shout")

    if first_char == '?' and remainder.endswith('?') and len(remainder) >= 2:
        inner = remainder[1:-1]
        if inner.startswith('"') and inner.endswith('"'):
            inner = inner[1:-1]
        return DialogueLine(character=character, text=inner, bubble_type="whisper")

    return None


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------


class CBMLParser:
    """
    Parser for CBML (Comic Book Markup Language) documents.

    Usage
    -----
    >>> parser = CBMLParser()
    >>> comic = parser.parse_file("my_comic.cbml")
    >>> comic = parser.parse_string(cbml_text)
    >>> result = parser.validate_file("my_comic.cbml")
    """

    def parse_file(
        self,
        path: str | Path,
        known_characters: list[str] | None = None,
        known_locations: list[str] | None = None,
        manga: bool = False,
    ) -> Comic:
        """
        Parse a CBML file from disk.

        Parameters
        ----------
        path : str | Path
        known_characters : list[str] | None
            Character identifiers to validate against (typically uploaded image filenames).
        known_locations : list[str] | None
            Location identifiers to validate against.
        manga : bool
            If True, reorganise the parsed comic into manga reading order
            (reversed pages, horizontally mirrored panels).

        Returns
        -------
        Comic

        Raises
        ------
        FileNotFoundError
        CBMLParseError
        CBMLValidationError
        """
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        return self.parse_string(
            text,
            known_characters=known_characters,
            known_locations=known_locations,
            manga=manga,
        )

    def parse_string(
        self,
        text: str,
        known_characters: list[str] | None = None,
        known_locations: list[str] | None = None,
        manga: bool = False,
    ) -> Comic:
        """
        Parse a CBML document from a string.

        Parameters
        ----------
        text : str
        known_characters : list[str] | None
        known_locations : list[str] | None
        manga : bool
            If True, reorganise the parsed comic into manga reading order
            (reversed pages, horizontally mirrored panels).

        Returns
        -------
        Comic

        Raises
        ------
        CBMLParseError
        CBMLValidationError
        """
        comic = self._parse(text)
        result = validate_comic(comic, known_characters=known_characters, known_locations=known_locations)
        if not result.valid:
            raise CBMLValidationError(errors=result.errors, warnings=result.warnings)
        comic.warnings = result.warnings
        if manga:
            comic = self.make_manga(comic)
        return comic

    def validate_file(
        self,
        path: str | Path,
        known_characters: list[str] | None = None,
        known_locations: list[str] | None = None,
    ) -> ValidationResult:
        """
        Validate a CBML file without raising on errors.

        Returns a ValidationResult containing errors and warnings.
        """
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        return self.validate_string(text, known_characters=known_characters, known_locations=known_locations)

    def validate_string(
        self,
        text: str,
        known_characters: list[str] | None = None,
        known_locations: list[str] | None = None,
    ) -> ValidationResult:
        """Validate a CBML string without raising on errors."""
        try:
            comic = self._parse(text)
        except (CBMLParseError, CBMLValidationError) as e:
            errors = e.errors if isinstance(e, CBMLValidationError) else [str(e)]
            return ValidationResult(valid=False, errors=errors, warnings=[])
        return validate_comic(comic, known_characters=known_characters, known_locations=known_locations)

    # ------------------------------------------------------------------
    # Manga transformation
    # ------------------------------------------------------------------

    _CAPTION_POS_HMIRROR: dict[str, str] = {
        "top-left": "top-right",
        "top-center": "top-center",
        "top-right": "top-left",
        "bottom-left": "bottom-right",
        "bottom-center": "bottom-center",
        "bottom-right": "bottom-left",
    }

    @staticmethod
    def make_manga(comic: Comic) -> Comic:
        """
        Return a deep copy of *comic* reorganised for manga (right-to-left)
        reading order.

        The transformation:
        1. **Page order** is reversed (last page becomes first).
        2. **Panel slots** are horizontally mirrored within each page's grid
           so that the rightmost panel becomes the leftmost.
        3. **Caption positions** are horizontally mirrored (e.g.
           ``top-left`` becomes ``top-right``).
        4. Page indices are re-numbered starting from 0.

        The original *comic* is not mutated.

        Parameters
        ----------
        comic : Comic
            A fully-parsed western-format comic.

        Returns
        -------
        Comic
            A new Comic in manga reading order.
        """
        manga_comic = copy.deepcopy(comic)

        # Reverse page order
        manga_comic.pages.reverse()

        for new_idx, page in enumerate(manga_comic.pages):
            page.index = new_idx

            # Determine grid column count
            if isinstance(page.layout, PresetLayout):
                max_cols = PRESET_LAYOUTS[page.layout.name]["grid"][0]
            else:
                max_cols = page.layout.cols

            # Mirror every slot horizontally
            for label, slot in page.slots.items():
                old_start, old_end = slot.cols
                slot.cols = (max_cols - old_end + 1, max_cols - old_start + 1)

            # Update each panel's slot reference & mirror captions
            for panel in page.panels:
                panel.slot = page.slots[panel.label]
                for caption in panel.captions:
                    caption.pos = CBMLParser._CAPTION_POS_HMIRROR.get(
                        caption.pos, caption.pos
                    )

        return manga_comic

    # ------------------------------------------------------------------
    # Internal parse implementation
    # ------------------------------------------------------------------

    def _parse(self, text: str) -> Comic:
        lines = text.splitlines()

        title: Optional[str] = None
        metadata: dict[str, str] = {}
        pages: list[Page] = []

        # Parser state
        in_header = True
        current_page: Optional[Page] = None
        current_panel: Optional[Panel] = None
        expecting_slots = False  # True after PAGE grid: until first PANEL

        def _finalise_panel():
            """Push the current panel onto the current page."""
            nonlocal current_panel
            if current_panel is not None and current_page is not None:
                # Strip and clean the action string
                current_panel.action = current_panel.action.strip()
                current_page.panels.append(current_panel)
                current_panel = None

        def _finalise_page():
            """Push the current page onto the pages list."""
            nonlocal current_page
            _finalise_panel()
            if current_page is not None:
                pages.append(current_page)
                current_page = None

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments (but not ## title lines)
            if not line:
                continue
            if line.startswith('#') and not line.startswith('## '):
                continue

            # ── Title (only valid when we haven't left the header) ──
            m = _RE_TITLE.match(line)
            if m:
                if title is not None:
                    raise CBMLParseError(
                        "Duplicate title declaration (## ...) found", line_number, raw_line
                    )
                title = m.group(1).strip()
                in_header = True
                continue

            # ── PAGE declaration ─────────────────────────────────────
            m_preset = _RE_PAGE_PRESET.match(line)
            m_grid = _RE_PAGE_GRID.match(line)

            if m_preset or m_grid:
                _finalise_page()
                in_header = False
                expecting_slots = False

                if title is None:
                    raise CBMLParseError(
                        "PAGE declaration found before comic title (## ...)",
                        line_number, raw_line,
                    )

                if m_preset:
                    preset_name = m_preset.group(1)
                    if preset_name not in PRESET_LAYOUTS:
                        raise CBMLParseError(
                            f"Unknown preset: {preset_name!r}. "
                            f"Valid presets: {', '.join(sorted(PRESET_LAYOUTS))}",
                            line_number, raw_line,
                        )
                    preset = PRESET_LAYOUTS[preset_name]
                    current_page = Page(
                        index=len(pages),
                        layout=PresetLayout(name=preset_name),
                        slots=dict(preset["slots"]),
                    )
                else:
                    cols = int(m_grid.group(1))
                    rows = int(m_grid.group(2))
                    if cols < 1 or rows < 1:
                        raise CBMLParseError(
                            "Grid dimensions must be positive integers",
                            line_number, raw_line,
                        )
                    current_page = Page(
                        index=len(pages),
                        layout=CustomGrid(cols=cols, rows=rows),
                        slots={},
                    )
                    expecting_slots = True
                continue

            # ── Slot definition ──────────────────────────────────────
            m = _RE_SLOT.match(line)
            if m:
                if current_page is None:
                    raise CBMLParseError(
                        "Slot definition found outside of a PAGE block",
                        line_number, raw_line,
                    )
                if isinstance(current_page.layout, PresetLayout):
                    raise CBMLParseError(
                        "Slot definitions must not follow a preset PAGE declaration",
                        line_number, raw_line,
                    )
                label = m.group(1)
                col_range = _parse_range(m.group(2), line_number, raw_line)
                row_range = _parse_range(m.group(3), line_number, raw_line)
                current_page.slots[label] = Slot(cols=col_range, rows=row_range)
                continue

            # ── PANEL declaration ────────────────────────────────────
            m = _RE_PANEL.match(line)
            if m:
                _finalise_panel()
                in_header = False
                expecting_slots = False

                if current_page is None:
                    raise CBMLParseError(
                        "PANEL declaration found outside of a PAGE block",
                        line_number, raw_line,
                    )

                panel_label = m.group(1)

                if panel_label not in current_page.slots:
                    raise CBMLParseError(
                        f"PANEL '{panel_label}' references an undefined slot. "
                        f"Defined slots: {', '.join(current_page.slots) or 'none'}",
                        line_number, raw_line,
                    )

                slot = current_page.slots[panel_label]
                current_panel = Panel(label=panel_label, slot=slot, loc="")
                continue

            # ── Panel fields (only valid inside a PANEL block) ───────

            if current_panel is not None:

                # loc:
                if line.startswith("loc:"):
                    current_panel.loc = line[4:].strip()
                    continue

                # chars:
                if line.startswith("chars:"):
                    raw_chars = line[6:].strip()
                    current_panel.chars = [c.strip() for c in raw_chars.split(",") if c.strip()]
                    continue

                # shot:
                if line.startswith("shot:"):
                    current_panel.shot = line[5:].strip()
                    continue

                # mood:
                if line.startswith("mood:"):
                    current_panel.mood = line[5:].strip()
                    continue

                # Action line
                if line.startswith("> "):
                    action_text = line[2:].strip()
                    if current_panel.action:
                        current_panel.action += " " + action_text
                    else:
                        current_panel.action = action_text
                    continue

                # Caption box
                m = _RE_CAPTION_BLOCK.match(line)
                if m:
                    attrs_str = m.group(1)
                    content = m.group(2)
                    caption = _parse_caption(content, attrs_str, line_number, raw_line)
                    current_panel.captions.append(caption)
                    continue

                # Dialogue line
                m = _RE_DIALOGUE.match(line)
                if m:
                    dl = _parse_dialogue(m, line_number, raw_line)
                    if dl is not None:
                        current_panel.dialogue.append(dl)
                        continue

            # ── Header fields (only in header section) ────────────────
            if in_header:
                m = _RE_HEADER_FIELD.match(line)
                if m:
                    key = m.group(1).lower()
                    value = m.group(2).strip()
                    if key in HEADER_FIELDS:
                        metadata[key] = value
                    # Unknown header fields silently ignored (validator warns)
                    continue

        # Finalise last page/panel
        _finalise_page()

        if title is None:
            raise CBMLParseError(
                "Document must begin with a title: ## Comic Title",
                1, lines[0] if lines else "",
            )

        return Comic(title=title, metadata=metadata, pages=pages)