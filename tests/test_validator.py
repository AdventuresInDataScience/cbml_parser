import pytest
from cbml_parser import CBMLParser, CBMLValidationError, CBMLParseError, Slot


# ---------------------------------------------------------------------------
# Slot.overlaps direct unit tests
# ---------------------------------------------------------------------------

class TestSlotOverlaps:

    def test_identical_slots_overlap(self):
        a = Slot((1, 2), (1, 2))
        b = Slot((1, 2), (1, 2))
        assert a.overlaps(b)

    def test_disjoint_columns_no_overlap(self):
        a = Slot((1, 1), (1, 1))
        b = Slot((2, 2), (1, 1))
        assert not a.overlaps(b)

    def test_disjoint_rows_no_overlap(self):
        a = Slot((1, 1), (1, 1))
        b = Slot((1, 1), (2, 2))
        assert not a.overlaps(b)

    def test_adjacent_no_overlap(self):
        a = Slot((1, 2), (1, 1))
        b = Slot((3, 4), (1, 1))
        assert not a.overlaps(b)

    def test_partial_column_overlap(self):
        a = Slot((1, 2), (1, 1))
        b = Slot((2, 3), (1, 1))
        assert a.overlaps(b)

    def test_single_cell_overlap(self):
        a = Slot((1, 3), (1, 3))
        b = Slot((3, 3), (3, 3))
        assert a.overlaps(b)

    def test_contained_slot_overlaps(self):
        """A small slot fully inside a larger one should overlap."""
        big = Slot((1, 4), (1, 4))
        small = Slot((2, 3), (2, 3))
        assert big.overlaps(small)
        assert small.overlaps(big)

    def test_overlap_is_symmetric(self):
        a = Slot((1, 2), (1, 2))
        b = Slot((2, 3), (2, 3))
        assert a.overlaps(b) == b.overlaps(a)


# ---------------------------------------------------------------------------
# _parse_range edge-case tests
# ---------------------------------------------------------------------------

class TestParseRangeEdgeCases:

    def test_single_value(self, parser):
        cbml = '''
## Range Test

PAGE grid:1x1
  A: [1, 1]

PANEL A
loc: room
> Simple.
'''
        comic = parser.parse_string(cbml)
        assert comic.pages[0].slots["A"].cols == (1, 1)
        assert comic.pages[0].slots["A"].rows == (1, 1)

    def test_range_value(self, parser):
        cbml = '''
## Range Test

PAGE grid:3x3
  A: [1-3, 1-3]

PANEL A
loc: room
> Full grid.
'''
        comic = parser.parse_string(cbml)
        assert comic.pages[0].slots["A"].cols == (1, 3)
        assert comic.pages[0].slots["A"].rows == (1, 3)

    def test_zero_range_rejected(self, parser):
        cbml = '''
## Range Test

PAGE grid:2x2
  A: [0, 1]

PANEL A
loc: room
> Bad range.
'''
        with pytest.raises(CBMLParseError):
            parser.parse_string(cbml)

    def test_inverted_range_rejected(self, parser):
        cbml = '''
## Range Test

PAGE grid:3x3
  A: [3-1, 1]

PANEL A
loc: room
> Inverted range.
'''
        with pytest.raises(CBMLParseError):
            parser.parse_string(cbml)


class TestValidationErrors:

    def test_missing_loc_raises(self, parser, fixture_path):
        result = parser.validate_file(fixture_path("invalid_missing_loc.cbml"))
        assert not result.valid
        assert any("loc" in e.lower() for e in result.errors)

    def test_dialogue_without_chars_raises(self, parser, fixture_path):
        result = parser.validate_file(fixture_path("invalid_dialogue_no_chars.cbml"))
        assert not result.valid
        assert any("chars" in e.lower() for e in result.errors)

    def test_undefined_slot_raises(self, parser, fixture_path):
        result = parser.validate_file(fixture_path("invalid_undefined_slot.cbml"))
        assert not result.valid
        assert any("Z" in e for e in result.errors)

    def test_dialogue_speaker_not_in_chars(self, parser):
        cbml = '''
## Speaker Test

PAGE preset:splash

PANEL A
loc: office
chars: ALICE
> Alice and Bob are here.
BOB: "Hello!"
'''
        result = parser.validate_string(cbml)
        assert not result.valid
        assert any("BOB" in e for e in result.errors)

    def test_overlapping_slots(self, parser):
        cbml = '''
## Overlap Test

PAGE grid:2x2
  A: [1-2, 1]
  B: [1, 1]

PANEL A
loc: room
> Panel A.

PANEL B
loc: room
> Panel B.
'''
        result = parser.validate_string(cbml)
        assert not result.valid
        assert any("overlap" in e.lower() for e in result.errors)

    def test_slot_defined_but_no_panel(self, parser):
        cbml = '''
## Missing Panel Test

PAGE grid:2x1
  A: [1, 1]
  B: [2, 1]

PANEL A
loc: room
> Only panel A is defined.
'''
        result = parser.validate_string(cbml)
        assert not result.valid
        assert any("B" in e for e in result.errors)

    def test_invalid_caption_hex(self, parser):
        cbml = '''
## Bad Caption

PAGE preset:splash

PANEL A
loc: room
> A panel.
[caption bg:#ZZZZZZ] Bad hex value.
'''
        with pytest.raises(Exception):
            parser.parse_string(cbml)

    def test_invalid_caption_pos(self, parser):
        cbml = '''
## Bad Caption Pos

PAGE preset:splash

PANEL A
loc: room
> A panel.
[caption pos:middle-somewhere] Bad position.
'''
        with pytest.raises(Exception):
            parser.parse_string(cbml)


class TestValidationWarnings:

    def test_unknown_character_generates_warning(self, parser):
        cbml = '''
## Warning Test

PAGE preset:splash

PANEL A
loc: forest
chars: GHOST
> A ghost in the forest.
'''
        result = parser.validate_string(cbml, known_characters=["KNOWN"])
        assert result.valid  # warnings don't block
        assert any("GHOST" in w for w in result.warnings)

    def test_unknown_location_generates_warning(self, parser):
        cbml = '''
## Warning Test

PAGE preset:splash

PANEL A
loc: unknown_place
> A panel with an unmatched location.
'''
        result = parser.validate_string(cbml, known_locations=["known_place"])
        assert result.valid
        assert any("unknown_place" in w for w in result.warnings)

    def test_no_warnings_with_matching_resources(self, parser):
        cbml = '''
## Clean Test

PAGE preset:splash

PANEL A
loc: forest_night
chars: HERO
> The hero in the forest.
'''
        result = parser.validate_string(
            cbml,
            known_characters=["HERO"],
            known_locations=["forest_night"],
        )
        assert result.valid
        assert result.warnings == []


class TestValidateVsParseString:

    def test_validate_returns_result_not_raises(self, parser):
        cbml = '''
## Invalid

PAGE preset:splash

PANEL A
> Missing loc.
'''
        result = parser.validate_string(cbml)
        assert isinstance(result.valid, bool)
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)

    def test_parse_raises_on_invalid(self, parser):
        cbml = '''
## Invalid

PAGE preset:splash

PANEL A
> Missing loc entirely.
'''
        with pytest.raises(CBMLValidationError) as exc_info:
            parser.parse_string(cbml)
        assert exc_info.value.errors