
# cbml-parser

A Python library for parsing [CBML (Comic Book Markup Language)](./docs/CBML_STANDARD.md) documents into structured data, ready for use in comic generation pipelines or any other downstream tooling.

---

## What is CBML?

CBML is a plain-text format for authoring comic books by hand. It defines page layouts, panel compositions, characters, locations, dialogue, and caption boxes in a lightweight, human-readable syntax. See the [CBML Standard](./docs/CBML_STANDARD.md) for the full language specification.

A CBML document looks like this:

```
## The Signal at Pier 9
author: A. Reyes
genre: mystery, coastal noir

PAGE preset:grid-2x2

PANEL A
loc: pier9_night_fog
chars: ELARA
shot: extreme wide, tiny figure on long pier, fog everywhere
mood: isolated, eerie
> Elara walks the length of Pier 9 alone. The fog is thicker than usual tonight.
[caption bg:#0a0f14 color:#a0c8d8 pos:top-left] 2:17 AM.

PANEL B
loc: pier9_night_fog
chars: ELARA
shot: medium shot, stopping mid-step
mood: the moment before something changes
> She stops. She heard something.

PANEL C
loc: lighthouse_radio_room
chars: ELARA
shot: closeup on old radio dial, needle moving
mood: impossible, wrong in the best way
> The dial reads the frequency of the Maren Clare. The ship that sank in 1983.

PANEL D
loc: lighthouse_radio_room
chars: ELARA
shot: closeup, receiver to her ear
> She picks up the receiver with both hands.
ELARA: ~Say something. Please say something.~
```

---

## Installation

```bash
pip install cbml-parser
```

---

## Quick Start

```python
from cbml_parser import CBMLParser

parser = CBMLParser()
comic = parser.parse_file("my_comic.cbml")
```

Or parse from a string directly:

```python
cbml_text = """
## My Comic
author: Jane Doe

PAGE preset:splash

PANEL A
loc: dark_forest
> A lone figure stands between the trees.
"""

comic = parser.parse_string(cbml_text)
```

---

## Worked Example

Given this CBML input:

```
## Ghost Signal
author: T. Navarro
genre: cyberpunk thriller

PAGE grid:3x2
  A: [1-2, 1]
  B: [3, 1-2]
  C: [1, 2]
  D: [2, 2]

PANEL A
loc: neon_alley_rain
chars: KAI
shot: wide, low angle, running toward camera
mood: desperate, urgent
> Kai sprints through the neon-lit alley, puddles exploding underfoot
[caption bg:#0d0d1a color:#ff4444 pos:top-left] Three minutes behind her. And closing.

PANEL B
loc: neon_alley_rain
chars: AGENT_CROSS
shot: closeup face, rain on visor
mood: cold, relentless
> Agent Cross raises one fist — a silent signal

PANEL C
loc: neon_alley_rain
chars: KAI
shot: over-the-shoulder, glancing back
> Kai looks back — blue strobes, closer than before

PANEL D
loc: neon_alley_rain
chars: KAI
shot: extreme closeup, eyes wide
> Her eyes: calculating, terrified, alive
KAI: ~Left. Always go left. Ghost taught me that.~
```

The parser produces the following structure:

```python
Comic(
    title="Ghost Signal",
    metadata={
        "author": "T. Navarro",
        "genre": "cyberpunk thriller"
    },
    pages=[
        Page(
            index=0,
            layout=CustomGrid(cols=3, rows=2),
            slots={
                "A": Slot(cols=(1,2), rows=(1,1)),
                "B": Slot(cols=(3,3), rows=(1,2)),
                "C": Slot(cols=(1,1), rows=(2,2)),
                "D": Slot(cols=(2,2), rows=(2,2))
            },
            panels=[
                Panel(
                    label="A",
                    slot=Slot(cols=(1,2), rows=(1,1)),
                    loc="neon_alley_rain",
                    chars=["KAI"],
                    shot="wide, low angle, running toward camera",
                    mood="desperate, urgent",
                    action="Kai sprints through the neon-lit alley, puddles exploding underfoot",
                    dialogue=[],
                    captions=[
                        Caption(
                            text="Three minutes behind her. And closing.",
                            bg="#0d0d1a",
                            color="#ff4444",
                            pos="top-left"
                        )
                    ]
                ),
                Panel(
                    label="B",
                    slot=Slot(cols=(3,3), rows=(1,2)),
                    loc="neon_alley_rain",
                    chars=["AGENT_CROSS"],
                    shot="closeup face, rain on visor",
                    mood="cold, relentless",
                    action="Agent Cross raises one fist — a silent signal",
                    dialogue=[],
                    captions=[]
                ),
                Panel(
                    label="C",
                    slot=Slot(cols=(1,1), rows=(2,2)),
                    loc="neon_alley_rain",
                    chars=["KAI"],
                    shot="over-the-shoulder, glancing back",
                    mood=None,
                    action="Kai looks back — blue strobes, closer than before",
                    dialogue=[],
                    captions=[]
                ),
                Panel(
                    label="D",
                    slot=Slot(cols=(2,2), rows=(2,2)),
                    loc="neon_alley_rain",
                    chars=["KAI"],
                    shot="extreme closeup, eyes wide",
                    mood=None,
                    action="Her eyes: calculating, terrified, alive",
                    dialogue=[
                        DialogueLine(
                            character="KAI",
                            text="Left. Always go left. Ghost taught me that.",
                            bubble_type="thought"
                        )
                    ],
                    captions=[]
                )
            ]
        )
    ]
)
```

---

## Validation

The parser validates documents against the CBML standard and reports errors and warnings:

```python
from cbml_parser import CBMLParser, CBMLValidationError

parser = CBMLParser()

try:
    comic = parser.parse_file("my_comic.cbml")
except CBMLValidationError as e:
    print(e.errors)    # list of blocking errors
    print(e.warnings)  # list of non-blocking warnings
```

Validation can also be run separately without full parsing:

```python
result = parser.validate_file("my_comic.cbml")
print(result.valid)
print(result.errors)
print(result.warnings)
```

---

## Passing Known Resources

To enable validation of character and location identifiers against known uploads, pass resource manifests to the parser:

```python
comic = parser.parse_file(
    "my_comic.cbml",
    known_characters=["KAI", "AGENT_CROSS", "NOVA"],
    known_locations=["neon_alley_rain", "construction_site_night"]
)
```

Unrecognised identifiers will generate warnings but will not block parsing.

---

## Manga / Right-to-Left Support

CBML documents are always written in western (left-to-right) reading order. To produce a manga-style comic, write your script forward as normal and pass `manga=True` at parse time:

```python
comic = parser.parse_file("my_manga.cbml", manga=True)
```

The parser will automatically:
- **Reverse page order** — your last page becomes the reader's first page
- **Mirror panel positions** — panels flip horizontally within each page grid
- **Mirror caption positions** — e.g. `top-left` becomes `top-right`

This keeps the `.cbml` source readable as a linear narrative while producing the correct physical layout for right-to-left reading.

You can also apply the transformation to an already-parsed comic:

```python
western_comic = parser.parse_file("my_comic.cbml")
manga_comic = CBMLParser.make_manga(western_comic)
```

See the [CBML Standard §12](./docs/CBML_STANDARD.md#12-reading-order-and-manga) for full details on the reading-order conventions.

---

## Documentation

- [CBML Standard](./docs/CBML_STANDARD.md) — The full language specification
- [API Reference](./docs/API_REFERENCE.md) — Complete Python API documentation

---

## License

MIT

---