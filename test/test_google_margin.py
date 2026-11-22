import pytest

import html2text


@pytest.mark.parametrize(
    "margin, depth",
    [
        ("auto", 0),
        ("inherit", 0),
        ("", 0),
        ("2em", 0),
        ("50%", 0),
        ("36px", 1),
        ("36pt", 1),
        ("72.5pt", 2),
        ("72.5px", 2),
        (" 36px ", 1),
        ("-36px", 0),
    ],
)
def test_google_list_margin(margin, depth):
    parser = html2text.HTML2Text()
    parser.google_doc = True
    parser.google_list_indent = 36
    assert parser.google_nest_count({"margin-left": margin}) == depth
    output = parser.handle(
        '<ul><li style="margin-left: {}">item</li></ul>'.format(margin)
    )
    assert "item" in output
