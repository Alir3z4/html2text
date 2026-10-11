import pytest

import html2text

# See https://github.com/Alir3z4/html2text/issues/163 for more information.


def test_newline_on_multiple_calls():
    h = html2text.HTML2Text()
    html = "<p>test</p>"
    md1 = h.handle(html)
    md2 = h.handle(html)
    md3 = h.handle(html)
    assert md1 == md2 == md3


@pytest.mark.parametrize("tag", ["em", "i", "u", "strong", "b", "del", "strike", "s"])
@pytest.mark.parametrize("text", ["hello", "hello*", "hello~"])
def test_emphasis_spacing_on_multiple_calls(tag, text):
    h = html2text.HTML2Text()
    source = "<{0}>{1}</{0}>".format(tag, text)
    expected = html2text.HTML2Text().handle(source)
    assert h.handle(source) == expected
    assert h.handle(source) == expected
    assert h.handle(source) == expected


def test_emphasis_spacing_does_not_leak_between_documents():
    h = html2text.HTML2Text()
    h.handle("previous document")
    assert h.handle("<em>next</em>") == "_next_\n\n"
