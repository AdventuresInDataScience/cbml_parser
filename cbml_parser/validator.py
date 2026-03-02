from __future__ import annotations
import re
from dataclasses import dataclass

from cbml_parser.models import Comic, Page, Panel, Caption
from cbml_parser.constants import VALID_CAPTION_POSITIONS


HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


@dataclass
class ValidationResult:
    """The outcome of a validation pass."""
    valid: bool
    errors: list[str]
    warnings: list[str]


def validate_comic(
    comic: Comic,
    known_characters: list[str] | None = None,
    known_locations: list[str] | None = None,
) -> ValidationResult:
    """
    Validate a fully parsed Comic object against the CBML standard.

    This is called automatically by CBMLParser after parsing. It can also
    be called independently to re-validate a Comic object.

    Parameters
    ----------
    comic : Comic
        The parsed comic to validate.
    known_characters : list[str] | None
        Optional list of uploaded character resource identifiers.
        Used to warn on unrecognised character names.
    known_locations : list[str] | None
        Optional list of uploaded location resource identifiers.
        Used to warn on unrecognised location identifiers.

    Returns
    -------
    ValidationResult
    """
    errors: list[str] = []
    warnings: list[str] = []

    known_chars = {c.upper() for c in (known_characters or [])}
    known_locs = {l.lower() for l in (known_locations or [])}

    # -- Document level --------------------------------------------------

    if not comic.title or not comic.title.strip():
        errors.append("Comic title is missing or empty.")

    if not comic.pages:
        errors.append("Document must contain at least one PAGE.")

    # -- Page level ------------------------------------------------------

    for page_idx, page in enumerate(comic.pages, start=1):
        page_label = f"Page {page_idx}"

        if not page.panels:
            errors.append(f"{page_label}: must contain at least one PANEL.")

        # Check every defined slot has a corresponding panel
        panel_labels = {p.label for p in page.panels}
        for slot_label in page.slots:
            if slot_label not in panel_labels:
                errors.append(
                    f"{page_label}: slot '{slot_label}' is defined but has no "
                    f"corresponding PANEL block."
                )

        # Check slot overlap
        slot_items = list(page.slots.items())
        for i, (label_a, slot_a) in enumerate(slot_items):
            for label_b, slot_b in slot_items[i + 1:]:
                if slot_a.overlaps(slot_b):
                    errors.append(
                        f"{page_label}: slots '{label_a}' and '{label_b}' overlap."
                    )

        # -- Panel level -------------------------------------------------

        for panel in page.panels:
            panel_label = f"{page_label}, Panel {panel.label}"

            # loc required
            if not panel.loc or not panel.loc.strip():
                errors.append(f"{panel_label}: 'loc:' is required but missing.")

            # chars required if dialogue present
            if panel.dialogue and not panel.chars:
                errors.append(
                    f"{panel_label}: 'chars:' is required when dialogue lines are present."
                )

            # each dialogue speaker must be in chars
            chars_upper = {c.upper() for c in panel.chars}
            for line in panel.dialogue:
                if line.character.upper() not in chars_upper:
                    errors.append(
                        f"{panel_label}: dialogue speaker '{line.character}' "
                        f"is not listed in 'chars:'."
                    )

            # caption attribute validation
            for i, caption in enumerate(panel.captions, start=1):
                cap_label = f"{panel_label}, caption {i}"
                if not HEX_RE.match(caption.bg):
                    errors.append(
                        f"{cap_label}: invalid hex colour for 'bg': {caption.bg!r}."
                    )
                if not HEX_RE.match(caption.color):
                    errors.append(
                        f"{cap_label}: invalid hex colour for 'color': {caption.color!r}."
                    )
                if caption.pos not in VALID_CAPTION_POSITIONS:
                    errors.append(
                        f"{cap_label}: invalid 'pos' value: {caption.pos!r}. "
                        f"Must be one of: {', '.join(sorted(VALID_CAPTION_POSITIONS))}."
                    )

            # Resource warnings (non-blocking)
            if known_locations and panel.loc.strip():
                if panel.loc.strip().lower() not in known_locs:
                    warnings.append(
                        f"{panel_label}: location '{panel.loc}' does not match "
                        f"any uploaded location resource."
                    )

            if known_characters:
                for char in panel.chars:
                    if char.upper() not in known_chars:
                        warnings.append(
                            f"{panel_label}: character '{char}' does not match "
                            f"any uploaded character resource."
                        )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )