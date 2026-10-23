import pytest

from html2text import HTML2Text


@pytest.mark.parametrize("width", [0, 20, 78])
@pytest.mark.parametrize("inline", [False, True])
def test_wrapping_preserves_link_style_between_documents(width, inline):
    parser = HTML2Text(bodywidth=width)
    parser.wrap_links = False
    parser.inline_links = inline
    source = '<a href="https://example.com">example</a>'
    first = parser.handle(source)
    assert parser.inline_links is inline
    second = parser.handle(source)
    assert parser.inline_links is inline
    if inline:
        assert "[example](https://example.com)" in first
        assert "[example](https://example.com)" in second
    else:
        assert "[example][" in first
        assert "[example][" in second
        assert ": https://example.com" in first
        assert ": https://example.com" in second
