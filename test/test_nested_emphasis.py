import pytest

import html2text


@pytest.mark.parametrize(
    "outer,inner,marker",
    [
        ("strong", "strong", "**"),
        ("b", "b", "**"),
        ("strong", "b", "**"),
        ("b", "strong", "**"),
        ("em", "em", "_"),
        ("i", "i", "_"),
        ("u", "u", "_"),
        ("em", "i", "_"),
        ("i", "u", "_"),
        ("u", "em", "_"),
    ],
)
def test_nested_emphasis_uses_one_pair_of_markers(outer, inner, marker):
    source = f"This tag shows <{outer}>bold<{inner}> text.</{inner}></{outer}>"
    expected = f"This tag shows {marker}bold text.{marker}\n\n"
    assert html2text.html2text(source) == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("<strong>bold <em>italic</em> bold</strong>", "**bold _italic_ bold**\n\n"),
        ("<em><strong>bold</strong> italic</em>", "_**bold** italic_\n\n"),
        ("<b>one</b> <strong>two</strong>", "**one** **two**\n\n"),
        ("<em>one</em> <i>two</i>", "_one_ _two_\n\n"),
    ],
)
def test_other_emphasis_keeps_its_markers(source, expected):
    assert html2text.html2text(source) == expected


def test_nested_emphasis_can_be_ignored():
    converter = html2text.HTML2Text()
    converter.ignore_emphasis = True
    assert converter.handle("<b>one<strong> two</strong></b>") == "one two\n\n"


def test_nested_emphasis_uses_configured_markers():
    converter = html2text.HTML2Text()
    converter.strong_mark = "__"
    converter.emphasis_mark = "*"
    source = "<b>one<strong> two</strong></b> <i>three<em> four</em></i>"
    assert converter.handle(source) == "__one two__ *three four*\n\n"


def test_deeply_nested_emphasis_stays_open_until_the_outer_end():
    source = "<strong>one <b>two <strong>three</strong> four</b> five</strong>"
    assert html2text.html2text(source) == "**one two three four five**\n\n"


@pytest.mark.parametrize("head_end", ["", "</head>"])
def test_body_recovers_after_ignored_head_emphasis(head_end):
    source = f"<head><b><em>{head_end}<body><b>bold</b> <em>italic</em>"
    assert html2text.html2text(source) == "**bold** _italic_\n\n"


@pytest.mark.parametrize("tag,marker", [("b", "**"), ("em", "_")])
def test_google_hidden_strike_does_not_suppress_later_emphasis(tag, marker):
    converter = html2text.HTML2Text()
    converter.google_doc = True
    converter.hide_strikethrough = True
    source = (
        f'<{tag} style="text-decoration:line-through">hidden</{tag}> '
        f"<{tag}>visible</{tag}>"
    )
    result = converter.handle(source)
    assert "hidden" not in result
    assert result.endswith(f"{marker}visible{marker}\n\n")
