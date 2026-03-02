from cbml_parser.models import Slot

# ---------------------------------------------------------------------------
# Preset layout definitions
# Each preset maps to a grid size and a dict of label -> Slot
# ---------------------------------------------------------------------------

PRESET_LAYOUTS: dict[str, dict] = {
    "splash": {
        "grid": (1, 1),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
        },
    },
    "strip-2": {
        "grid": (2, 1),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
        },
    },
    "strip-3": {
        "grid": (3, 1),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((3, 3), (1, 1)),
        },
    },
    "strip-4": {
        "grid": (4, 1),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((3, 3), (1, 1)),
            "D": Slot((4, 4), (1, 1)),
        },
    },
    "grid-2x2": {
        "grid": (2, 2),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((1, 1), (2, 2)),
            "D": Slot((2, 2), (2, 2)),
        },
    },
    "grid-2x3": {
        "grid": (2, 3),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((1, 1), (2, 2)),
            "D": Slot((2, 2), (2, 2)),
            "E": Slot((1, 1), (3, 3)),
            "F": Slot((2, 2), (3, 3)),
        },
    },
    "grid-3x2": {
        "grid": (3, 2),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((3, 3), (1, 1)),
            "D": Slot((1, 1), (2, 2)),
            "E": Slot((2, 2), (2, 2)),
            "F": Slot((3, 3), (2, 2)),
        },
    },
    # Large left panel, two stacked right
    "feature-left": {
        "grid": (3, 2),
        "slots": {
            "A": Slot((1, 2), (1, 2)),
            "B": Slot((3, 3), (1, 1)),
            "C": Slot((3, 3), (2, 2)),
        },
    },
    # Two stacked left, large right panel
    "feature-right": {
        "grid": (3, 2),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((1, 1), (2, 2)),
            "C": Slot((2, 3), (1, 2)),
        },
    },
    # Wide top, three equal below
    "feature-top": {
        "grid": (3, 2),
        "slots": {
            "A": Slot((1, 3), (1, 1)),
            "B": Slot((1, 1), (2, 2)),
            "C": Slot((2, 2), (2, 2)),
            "D": Slot((3, 3), (2, 2)),
        },
    },
    # Three equal top, wide bottom
    "feature-bottom": {
        "grid": (3, 2),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((3, 3), (1, 1)),
            "D": Slot((1, 3), (2, 2)),
        },
    },
    # Wide top, two equal below
    "wide-top": {
        "grid": (2, 2),
        "slots": {
            "A": Slot((1, 2), (1, 1)),
            "B": Slot((1, 1), (2, 2)),
            "C": Slot((2, 2), (2, 2)),
        },
    },
    # Two equal top, wide bottom
    "wide-bottom": {
        "grid": (2, 2),
        "slots": {
            "A": Slot((1, 1), (1, 1)),
            "B": Slot((2, 2), (1, 1)),
            "C": Slot((1, 2), (2, 2)),
        },
    },
}

# ---------------------------------------------------------------------------
# Valid caption position values
# ---------------------------------------------------------------------------

VALID_CAPTION_POSITIONS: frozenset[str] = frozenset({
    "top-left",
    "top-center",
    "top-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
})

# ---------------------------------------------------------------------------
# Reserved keywords — must not be used as panel labels, char IDs, loc IDs
# ---------------------------------------------------------------------------

RESERVED_KEYWORDS: frozenset[str] = frozenset({
    "PAGE", "PANEL", "preset", "grid",
    "loc", "chars", "shot", "mood",
    "author", "genre", "description", "caption",
})

# ---------------------------------------------------------------------------
# Header fields recognised beyond title
# ---------------------------------------------------------------------------

HEADER_FIELDS: frozenset[str] = frozenset({
    "author", "genre", "description",
})

# ---------------------------------------------------------------------------
# Bubble type markers
# ---------------------------------------------------------------------------

BUBBLE_TYPES: dict[str, str] = {
    '"': "speech",
    "~": "thought",
    "!": "shout",
    "?": "whisper",
}