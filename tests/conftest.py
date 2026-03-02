from pathlib import Path
import pytest
from cbml_parser import CBMLParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def parser():
    return CBMLParser()


@pytest.fixture
def fixture_path():
    def _get(name: str) -> Path:
        return FIXTURES_DIR / name
    return _get


@pytest.fixture
def parse_fixture(parser, fixture_path):
    """Convenience fixture: parse a named fixture file and return the Comic."""
    def _parse(name: str, **kwargs):
        return parser.parse_file(fixture_path(name), **kwargs)
    return _parse