import pytest
from cbml_parser import CBMLParser, CBMLValidationError


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