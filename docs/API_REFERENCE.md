
# cbml-parser — API Reference

> **Status: Draft.** This document describes the intended API. It will be fully expanded with complete method signatures, return type details, and extended examples once the implementation is complete.

---

## Overview

The `cbml-parser` library exposes a primary `CBMLParser` class for parsing and validating CBML documents, and a set of dataclasses representing the parsed document structure.

---

## Module Structure

```
cbml_parser/
├── parser.py         # CBMLParser class
├── models.py         # Comic, Page, Panel, and related dataclasses
├── validator.py      # Validation logic and ValidationResult
├── exceptions.py     # CBMLValidationError and related exceptions
└── constants.py      # Preset definitions, reserved keywords
```

---

## Classes (Outline)

### `CBMLParser`
Primary entry point. Exposes `parse_file()`, `parse_string()`, `validate_file()` / `validate_string()`, and `make_manga()`.

### `Comic`
Top-level dataclass. Contains `title`, `metadata`, `warnings`, and a list of `Page` objects.

### `Page`
Represents a single page. Contains `index`, `layout` (either `PresetLayout` or `CustomGrid`), `slots`, and a list of `Panel` objects.

### `Panel`
Represents a single panel. Contains `label`, `slot`, `loc`, `chars`, `shot`, `mood`, `action`, `dialogue` (list of `DialogueLine`), and `captions` (list of `Caption`).

### `DialogueLine`
Contains `character`, `text`, and `bubble_type` (one of `"speech"`, `"thought"`, `"shout"`, `"whisper"`).

### `Caption`
Contains `text`, `bg`, `color`, and `pos`.

### `Slot`
Contains `cols` (tuple of start, end) and `rows` (tuple of start, end).

### `ValidationResult`
Contains `valid` (bool), `errors` (list of strings), `warnings` (list of strings).

### `CBMLValidationError`
Exception raised on parse failure. Contains `errors` and `warnings`.

---

## Method Reference

### `CBMLParser.parse_file(path, *, known_characters=None, known_locations=None, manga=False)`

Parse a `.cbml` file from disk.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str \| Path` | — | Path to the CBML file |
| `known_characters` | `list[str] \| None` | `None` | Character IDs to validate against |
| `known_locations` | `list[str] \| None` | `None` | Location IDs to validate against |
| `manga` | `bool` | `False` | If `True`, transform the result into manga (right-to-left) reading order |

**Returns:** `Comic`

**Raises:** `FileNotFoundError`, `CBMLParseError`, `CBMLValidationError`

---

### `CBMLParser.parse_string(text, *, known_characters=None, known_locations=None, manga=False)`

Parse a CBML document from a string.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | — | The CBML source text |
| `known_characters` | `list[str] \| None` | `None` | Character IDs to validate against |
| `known_locations` | `list[str] \| None` | `None` | Location IDs to validate against |
| `manga` | `bool` | `False` | If `True`, transform the result into manga reading order |

**Returns:** `Comic`

**Raises:** `CBMLParseError`, `CBMLValidationError`

---

### `CBMLParser.validate_file(path, *, known_characters=None, known_locations=None)`

Validate a `.cbml` file without raising on errors.

**Returns:** `ValidationResult`

---

### `CBMLParser.validate_string(text, *, known_characters=None, known_locations=None)`

Validate a CBML string without raising on errors.

**Returns:** `ValidationResult`

---

### `CBMLParser.make_manga(comic)` (static method)

Return a deep copy of a western-format `Comic` reorganised into manga (right-to-left) reading order.

The transformation:
1. **Page order reversed** — the last page becomes the first.
2. **Panel slots horizontally mirrored** — column positions are flipped within each page's grid so the rightmost panel becomes the leftmost.
3. **Caption positions mirrored** — e.g. `top-left` → `top-right`, `bottom-right` → `bottom-left`. Centre positions are unchanged.
4. **Page indices re-numbered** starting from 0.

The original `comic` is **not** mutated.

| Parameter | Type | Description |
|---|---|---|
| `comic` | `Comic` | A fully-parsed western-format comic |

**Returns:** `Comic` — a new `Comic` in manga reading order.

**Example:**

```python
parser = CBMLParser()

# Option A: transform at parse time
manga = parser.parse_file("my_comic.cbml", manga=True)

# Option B: transform after the fact
western = parser.parse_file("my_comic.cbml")
manga = CBMLParser.make_manga(western)
```