import pytest

from html2text import HTML2Text
from html2text.utils import escape_md_section


@pytest.mark.parametrize("text", ["* item", "> quote", "# title", "###### title"])
def test_escape_plain_block_markers(text):
    assert escape_md_section(text) == "\\" + text
    assert escape_md_section("  " + text) == "  \\" + text


@pytest.mark.parametrize(
    "source, expected",
    [
        ("* item", r"\* item"),
        ("&ast; item", r"\* item"),
        ("&#42; item", r"\* item"),
        ("&#x2a; item", r"\* item"),
        ("&gt; quote", r"\> quote"),
        ("&#62; quote", r"\> quote"),
        ("&#x3e; quote", r"\> quote"),
        ("# title", r"\# title"),
        ("&num; title", r"\# title"),
        ("&#35; title", r"\# title"),
        ("&#x23; title", r"\# title"),
        ("###### title", r"\###### title"),
        ("&#35;&#35; title", r"\## title"),
        ("<span>*</span> item", r"\* item"),
        ("<span>#</span> title", r"\# title"),
        ("<span>&gt;</span> quote", r"\> quote"),
    ],
)
def test_paragraph_block_markers(source, expected):
    converter = HTML2Text(bodywidth=0)
    assert converter.handle("<p>" + source + "</p>").strip() == expected
    assert converter.handle("<p>First</p><p>" + source + "</p>").strip() == (
        "First\n\n" + expected
    )


@pytest.mark.parametrize(
    "source, expected",
    [
        ("<h1>Heading</h1>", "# Heading"),
        ("<ul><li>item</li></ul>", "* item"),
        ("<blockquote>quote</blockquote>", "> quote"),
        ("<code>* code</code>", "`* code`"),
        ("<code>&gt; code</code>", "`> code`"),
        ("<p>inline * item &gt; quote # title</p>", "inline * item > quote # title"),
    ],
)
def test_generated_markup_and_inline_code_are_preserved(source, expected):
    assert HTML2Text(bodywidth=0).handle(source).strip() == expected


def test_preformatted_block_markers_are_preserved():
    assert HTML2Text(bodywidth=0).handle("<pre>* code\n&gt; code\n# code</pre>") == (
        "\n    * code\n    > code\n    # code\n"
    )


def test_escape_snob_does_not_double_escape_markers():
    converter = HTML2Text(bodywidth=0)
    converter.escape_snob = True
    assert converter.handle("<p>* item</p><p># title</p>").strip() == (
        "\\* item\n\n\\# title"
    )
