
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
Primary entry point. Exposes `parse_file()`, `parse_string()`, and `validate_file()` / `validate_string()`.

### `Comic`
Top-level dataclass. Contains `title`, `metadata`, and a list of `Page` objects.

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