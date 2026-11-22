import pytest

import html2text


@pytest.mark.parametrize(
    "tag,marker", [("b", "**"), ("strong", "**"), ("em", "_"), ("i", "_"), ("u", "_")]
)
@pytest.mark.parametrize("space", [" ", "\n", "\t", ""])
def test_space_before_link_inside_emphasis(tag, marker, space):
    source = '<{0}>This is{1}<a href="/target">a link</a> here</{0}>'.format(tag, space)
    expected_space = " " if space else ""
    expected = "{0}This is{1}[a link](/target) here{0}\n\n".format(
        marker, expected_space
    )
    assert html2text.html2text(source) == expected


@pytest.mark.parametrize("automatic", [True, False])
def test_space_before_automatic_link_inside_emphasis(automatic):
    parser = html2text.HTML2Text()
    parser.use_automatic_links = automatic
    source = '<b>Visit <a href="https://example.com">https://example.com</a></b>'
    link = (
        "<https://example.com>"
        if automatic
        else "[https://example.com](https://example.com)"
    )
    assert parser.handle(source) == "**Visit " + link + "**\n\n"


def test_no_space_at_start_of_emphasized_link():
    source = '<b><a href="/target">a link</a></b>'
    assert html2text.html2text(source) == "**[a link](/target)**\n\n"
