from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class Slot:
    """A named region of the grid assigned to a panel."""
    cols: tuple[int, int]  # (start, end) inclusive, 1-indexed
    rows: tuple[int, int]  # (start, end) inclusive, 1-indexed

    def overlaps(self, other: Slot) -> bool:
        col_overlap = self.cols[0] <= other.cols[1] and self.cols[1] >= other.cols[0]
        row_overlap = self.rows[0] <= other.rows[1] and self.rows[1] >= other.rows[0]
        return col_overlap and row_overlap


@dataclass
class DialogueLine:
    """A single dialogue line attributed to a character."""
    character: str
    text: str
    bubble_type: str  # "speech" | "thought" | "shout" | "whisper"


@dataclass
class Caption:
    """A narrator text box overlaid on a panel."""
    text: str
    bg: str = "#000000"
    color: str = "#ffffff"
    pos: str = "top-left"


@dataclass
class Panel:
    """A single framed image unit within a page."""
    label: str
    slot: Slot
    loc: str
    chars: list[str] = field(default_factory=list)
    shot: Optional[str] = None
    mood: Optional[str] = None
    action: str = ""
    dialogue: list[DialogueLine] = field(default_factory=list)
    captions: list[Caption] = field(default_factory=list)


@dataclass
class PresetLayout:
    """A named standard layout shorthand."""
    name: str


@dataclass
class CustomGrid:
    """A user-defined column/row grid."""
    cols: int
    rows: int


@dataclass
class Page:
    """A single comic book page."""
    index: int
    layout: Union[PresetLayout, CustomGrid]
    slots: dict[str, Slot]
    panels: list[Panel] = field(default_factory=list)


@dataclass
class Comic:
    """The top-level parsed CBML document."""
    title: str
    metadata: dict[str, str]
    pages: list[Page] = field(default_factory=list)