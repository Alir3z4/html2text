import pytest

from html2text import html2text


@pytest.mark.parametrize(
    "attribute, number",
    [("start", 1), ('start=""', 1), ('start="invalid"', 1), ('start="3"', 3)],
)
def test_ordered_list_start(attribute, number):
    result = html2text(f"<ol {attribute}><li>First</li><li>Second</li></ol>")

    assert result == f"  {number}. First\n  {number + 1}. Second\n\n"
