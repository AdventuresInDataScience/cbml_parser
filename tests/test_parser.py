import pytest
from cbml_parser import (
    CBMLParser,
    CBMLParseError,
    CBMLValidationError,
    Comic,
    Page,
    Panel,
    PresetLayout,
    CustomGrid,
    Slot,
    DialogueLine,
    Caption,
)


# ---------------------------------------------------------------------------
# Minimal document
# ---------------------------------------------------------------------------

class TestMinimalDocument:

    def test_parses_title(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert comic.title == "Untitled"

    def test_returns_comic_instance(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert isinstance(comic, Comic)

    def test_single_page(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert len(comic.pages) == 1

    def test_single_panel(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert len(comic.pages[0].panels) == 1

    def test_panel_loc(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert comic.pages[0].panels[0].loc == "a dark room"

    def test_panel_action(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        assert "darkness" in comic.pages[0].panels[0].action

    def test_no_chars_no_dialogue(self, parse_fixture):
        comic = parse_fixture("minimal.cbml")
        panel = comic.pages[0].panels[0]
        assert panel.chars == []
        assert panel.dialogue == []


# ---------------------------------------------------------------------------
# Preset layout
# ---------------------------------------------------------------------------

class TestPresetLayout:

    def test_metadata(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        assert comic.metadata["author"] == "J. Okafor"
        assert comic.metadata["genre"] == "drama"

    def test_preset_layout_type(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        assert isinstance(comic.pages[0].layout, PresetLayout)
        assert comic.pages[0].layout.name == "grid-2x2"

    def test_four_panels(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        assert len(comic.pages[0].panels) == 4

    def test_panel_labels(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        labels = [p.label for p in comic.pages[0].panels]
        assert labels == ["A", "B", "C", "D"]

    def test_panel_chars_single(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        panel_a = comic.pages[0].panels[0]
        assert panel_a.chars == ["MAYA"]

    def test_panel_chars_multiple(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        panel_c = comic.pages[0].panels[2]
        assert set(panel_c.chars) == {"MAYA", "DANIEL"}

    def test_panel_shot(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        assert comic.pages[0].panels[0].shot == "medium shot, profile"

    def test_panel_mood(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        assert "melancholy" in comic.pages[0].panels[0].mood

    def test_dialogue_speech(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        panel_d = comic.pages[0].panels[3]
        assert len(panel_d.dialogue) == 1
        dl = panel_d.dialogue[0]
        assert dl.character == "MAYA"
        assert dl.text == "You should probably go."
        assert dl.bubble_type == "speech"

    def test_caption_parsed(self, parse_fixture):
        comic = parse_fixture("single_page_preset.cbml")
        panel_a = comic.pages[0].panels[0]
        assert len(panel_a.captions) == 1
        cap = panel_a.captions[0]
        assert cap.text == "6:43 AM."
        assert cap.bg == "#111111"
        assert cap.color == "#cccccc"
        assert cap.pos == "top-left"


# ---------------------------------------------------------------------------
# Custom grid, multi-page
# ---------------------------------------------------------------------------

class TestCustomGridMultiPage:

    def test_two_pages(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        assert len(comic.pages) == 2

    def test_first_page_custom_grid(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        layout = comic.pages[0].layout
        assert isinstance(layout, CustomGrid)
        assert layout.cols == 3
        assert layout.rows == 2

    def test_slot_dimensions(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        slots = comic.pages[0].slots
        # A: [1-2, 1]
        assert slots["A"].cols == (1, 2)
        assert slots["A"].rows == (1, 1)
        # B: [3, 1-2]
        assert slots["B"].cols == (3, 3)
        assert slots["B"].rows == (1, 2)

    def test_first_page_panel_count(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        assert len(comic.pages[0].panels) == 4

    def test_second_page_panel_count(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        assert len(comic.pages[1].panels) == 4

    def test_thought_bubble(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        panel_d = comic.pages[0].panels[3]
        assert panel_d.dialogue[0].bubble_type == "thought"
        assert "Ghost taught me that" in panel_d.dialogue[0].text

    def test_whisper_bubble(self, parse_fixture):
        comic = parse_fixture("multi_page_action.cbml")
        panel_b_p2 = comic.pages[1].panels[1]
        assert panel_b_p2.dialogue[0].bubble_type == "whisper"

    def test_action_multi_line_concatenation(self, parser):
        cbml = """
## Test

PAGE preset:splash

PANEL A
loc: forest
> The trees stretch endlessly upward.
> Roots crack through ancient stone below.
> There is no sky visible from here.
"""
        comic = parser.parse_string(cbml)
        action = comic.pages[0].panels[0].action
        assert "trees stretch" in action
        assert "ancient stone" in action
        assert "no sky" in action


# ---------------------------------------------------------------------------
# Splash page narration
# ---------------------------------------------------------------------------

class TestSplashNarration:

    def test_splash_preset(self, parse_fixture):
        comic = parse_fixture("splash_narration.cbml")
        assert comic.pages[0].layout.name == "splash"

    def test_three_captions(self, parse_fixture):
        comic = parse_fixture("splash_narration.cbml")
        panel = comic.pages[0].panels[0]
        assert len(panel.captions) == 3

    def test_caption_colours(self, parse_fixture):
        comic = parse_fixture("splash_narration.cbml")
        captions = comic.pages[0].panels[0].captions
        assert captions[0].color == "#aaddff"
        assert captions[2].color == "#ffffff"
        assert captions[2].pos == "bottom-right"

    def test_no_dialogue(self, parse_fixture):
        comic = parse_fixture("splash_narration.cbml")
        assert comic.pages[0].panels[0].dialogue == []


# ---------------------------------------------------------------------------
# Dialogue-heavy scene
# ---------------------------------------------------------------------------

class TestDialogueHeavy:

    def test_six_panels(self, parse_fixture):
        comic = parse_fixture("dialogue_heavy.cbml")
        assert len(comic.pages[0].panels) == 6

    def test_multiple_dialogue_same_character(self, parse_fixture):
        comic = parse_fixture("dialogue_heavy.cbml")
        panel_b = comic.pages[0].panels[1]
        hara_lines = [d for d in panel_b.dialogue if d.character == "DETECTIVE_HARA"]
        assert len(hara_lines) == 2

    def test_whisper_type(self, parse_fixture):
        comic = parse_fixture("dialogue_heavy.cbml")
        panel_d = comic.pages[0].panels[3]
        assert panel_d.dialogue[0].bubble_type == "whisper"

    def test_multiple_speakers_in_panel(self, parse_fixture):
        comic = parse_fixture("dialogue_heavy.cbml")
        panel_e = comic.pages[0].panels[4]
        speakers = [d.character for d in panel_e.dialogue]
        assert speakers == ["VINCENT", "VINCENT"]


# ---------------------------------------------------------------------------
# Inline parse_string edge cases
# ---------------------------------------------------------------------------

class TestParseString:

    def test_shout_bubble(self, parser):
        cbml = '''
## Shout Test

PAGE preset:splash

PANEL A
loc: arena
chars: HERO
> Hero stands in the arena.
HERO: !"For glory!"!
'''
        comic = parser.parse_string(cbml)
        dl = comic.pages[0].panels[0].dialogue[0]
        assert dl.bubble_type == "shout"
        assert dl.text == "For glory!"

    def test_optional_fields_default_to_none(self, parser):
        cbml = '''
## Defaults Test

PAGE preset:splash

PANEL A
loc: forest
> Just an action line.
'''
        comic = parser.parse_string(cbml)
        panel = comic.pages[0].panels[0]
        assert panel.shot is None
        assert panel.mood is None
        assert panel.chars == []
        assert panel.dialogue == []
        assert panel.captions == []

    def test_comments_ignored(self, parser):
        cbml = '''
# This is a file-level comment
## Comment Test
# author comment
author: Test Author

# Page comment
PAGE preset:splash

# Panel comment
PANEL A
loc: office
# action comment
> A figure types at a desk.
'''
        comic = parser.parse_string(cbml)
        assert comic.title == "Comment Test"
        assert comic.metadata["author"] == "Test Author"
        assert len(comic.pages[0].panels) == 1

    def test_caption_default_attributes(self, parser):
        cbml = '''
## Caption Defaults

PAGE preset:splash

PANEL A
loc: void
> Emptiness.
[caption] Just some text.
'''
        comic = parser.parse_string(cbml)
        cap = comic.pages[0].panels[0].captions[0]
        assert cap.bg == "#000000"
        assert cap.color == "#ffffff"
        assert cap.pos == "top-left"
        assert cap.text == "Just some text."

    def test_caption_partial_attributes(self, parser):
        cbml = '''
## Caption Partial

PAGE preset:splash

PANEL A
loc: void
> Nothing.
[caption pos:bottom-right] Positioned caption.
'''
        comic = parser.parse_string(cbml)
        cap = comic.pages[0].panels[0].captions[0]
        assert cap.pos == "bottom-right"
        assert cap.bg == "#000000"   # default
        assert cap.color == "#ffffff"  # default

    def test_genre_and_description_metadata(self, parser):
        cbml = '''
## Metadata Test
author: Someone
genre: horror
description: A tale of quiet dread.

PAGE preset:splash

PANEL A
loc: a dark corridor
> Nothing moves.
'''
        comic = parser.parse_string(cbml)
        assert comic.metadata["genre"] == "horror"
        assert comic.metadata["description"] == "A tale of quiet dread."

    def test_known_characters_warning_not_error(self, parser):
        cbml = '''
## Known Chars Test

PAGE preset:splash

PANEL A
loc: forest
chars: UNKNOWN_CHAR
> A stranger in the woods.
'''
        # Should not raise — unknown char is a warning only
        comic = parser.parse_string(cbml, known_characters=["KNOWN_CHAR"])
        assert comic.pages[0].panels[0].chars == ["UNKNOWN_CHAR"]

    def test_warnings_preserved_on_comic(self, parser):
        cbml = '''
## Warnings Preserved

PAGE preset:splash

PANEL A
loc: forest
chars: GHOST
> A ghost in the forest.
'''
        comic = parser.parse_string(cbml, known_characters=["KNOWN"])
        assert any("GHOST" in w for w in comic.warnings)


# ---------------------------------------------------------------------------
# Manga transformation
# ---------------------------------------------------------------------------

class TestMakeManga:

    def test_page_order_reversed(self, parse_fixture):
        """Multi-page fixture pages should appear in reverse order."""
        western = parse_fixture("multi_page_action.cbml")
        manga = CBMLParser.make_manga(western)
        assert len(manga.pages) == 2
        # The second western page is now first
        assert manga.pages[0].index == 0
        assert manga.pages[1].index == 1
        # Verify by checking a location unique to each page
        assert manga.pages[0].panels[0].loc == "construction_site_night"
        assert manga.pages[1].panels[0].loc == "neon_alley_rain"

    def test_page_indices_renumbered(self, parser):
        cbml = '''
## Manga Index Test

PAGE preset:splash

PANEL A
loc: room_one
> Page 1.

PAGE preset:splash

PANEL A
loc: room_two
> Page 2.

PAGE preset:splash

PANEL A
loc: room_three
> Page 3.
'''
        western = parser.parse_string(cbml)
        manga = CBMLParser.make_manga(western)
        assert [p.index for p in manga.pages] == [0, 1, 2]
        assert manga.pages[0].panels[0].loc == "room_three"

    def test_slots_mirrored_horizontally(self, parser):
        cbml = '''
## Mirror Test

PAGE grid:3x2
  A: [1, 1]
  B: [2-3, 1]
  C: [1-3, 2]

PANEL A
loc: room
> A.

PANEL B
loc: room
> B.

PANEL C
loc: room
> C.
'''
        western = parser.parse_string(cbml)
        manga = CBMLParser.make_manga(western)
        slots = manga.pages[0].slots
        # A was col (1,1) in a 3-col grid → mirrored to (3,3)
        assert slots["A"].cols == (3, 3)
        assert slots["A"].rows == (1, 1)
        # B was col (2,3) → mirrored to (1,2)
        assert slots["B"].cols == (1, 2)
        assert slots["B"].rows == (1, 1)
        # C was col (1,3) → mirrored to (1,3) — full-width stays full-width
        assert slots["C"].cols == (1, 3)
        assert slots["C"].rows == (2, 2)

    def test_panel_slot_refs_updated(self, parser):
        cbml = '''
## Slot Ref Test

PAGE grid:2x1
  A: [1, 1]
  B: [2, 1]

PANEL A
loc: left
> Left panel.

PANEL B
loc: right
> Right panel.
'''
        western = parser.parse_string(cbml)
        manga = CBMLParser.make_manga(western)
        panel_a = manga.pages[0].panels[0]
        panel_b = manga.pages[0].panels[1]
        # A was col (1,1) → mirrored to (2,2); B was (2,2) → (1,1)
        assert panel_a.slot.cols == (2, 2)
        assert panel_b.slot.cols == (1, 1)

    def test_caption_positions_mirrored(self, parser):
        cbml = '''
## Caption Mirror

PAGE preset:splash

PANEL A
loc: room
> Action.
[caption pos:top-left] Left caption.
[caption pos:bottom-right] Right caption.
[caption pos:top-center] Centre caption.
'''
        western = parser.parse_string(cbml)
        manga = CBMLParser.make_manga(western)
        caps = manga.pages[0].panels[0].captions
        assert caps[0].pos == "top-right"
        assert caps[1].pos == "bottom-left"
        assert caps[2].pos == "top-center"

    def test_preset_layout_mirrored(self, parser):
        cbml = '''
## Preset Mirror

PAGE preset:grid-2x2

PANEL A
loc: top_left
> A.

PANEL B
loc: top_right
> B.

PANEL C
loc: bottom_left
> C.

PANEL D
loc: bottom_right
> D.
'''
        western = parser.parse_string(cbml)
        manga = CBMLParser.make_manga(western)
        slots = manga.pages[0].slots
        # grid-2x2: A(1,1)(1,1) B(2,2)(1,1) C(1,1)(2,2) D(2,2)(2,2)
        # Mirrored:  A→(2,2)(1,1) B→(1,1)(1,1) C→(2,2)(2,2) D→(1,1)(2,2)
        assert slots["A"].cols == (2, 2)
        assert slots["B"].cols == (1, 1)
        assert slots["C"].cols == (2, 2)
        assert slots["D"].cols == (1, 1)

    def test_original_comic_not_mutated(self, parser):
        cbml = '''
## Immutability Test

PAGE preset:grid-2x2

PANEL A
loc: room
> A.

PANEL B
loc: room
> B.

PANEL C
loc: room
> C.

PANEL D
loc: room
> D.
'''
        western = parser.parse_string(cbml)
        original_a_cols = western.pages[0].slots["A"].cols
        CBMLParser.make_manga(western)
        assert western.pages[0].slots["A"].cols == original_a_cols

    def test_manga_flag_on_parse_string(self, parser):
        cbml = '''
## Flag Test

PAGE preset:splash

PANEL A
loc: room
> Action.

PAGE preset:splash

PANEL A
loc: other_room
> Action.
'''
        comic = parser.parse_string(cbml, manga=True)
        assert comic.pages[0].panels[0].loc == "other_room"
        assert comic.pages[1].panels[0].loc == "room"

    def test_manga_flag_on_parse_file(self, parse_fixture):
        """parse_file with manga=True should also reverse pages."""
        western = parse_fixture("multi_page_action.cbml")
        manga = parse_fixture("multi_page_action.cbml", manga=True)
        assert manga.pages[0].panels[0].loc == western.pages[-1].panels[0].loc