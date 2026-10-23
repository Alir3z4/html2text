import pytest

from html2text import HTML2Text
from html2text.utils import skipwrap


@pytest.mark.parametrize("marker", ["1.", "+", "*", "-"])
@pytest.mark.parametrize("enabled", [False, True])
def test_wrap_list_items_controls_list_markers(marker, enabled):
    assert skipwrap(marker + " one two three", True, enabled, False) is not enabled


@pytest.mark.parametrize("enabled", [False, True])
def test_wrap_ordered_list_items(enabled):
    parser = HTML2Text(bodywidth=20)
    parser.wrap_list_items = enabled
    text = "one two three four five six seven eight nine ten"
    output = parser.handle("<ol><li>" + text + "</li></ol>")
    assert " ".join(output.split()) == "1. " + text
    if enabled:
        assert all(len(line) <= 20 for line in output.splitlines())
    else:
        assert "1. " + text in output
