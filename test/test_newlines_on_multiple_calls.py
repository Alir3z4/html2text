import html2text

# See https://github.com/Alir3z4/html2text/issues/163 for more information.


def test_newline_on_multiple_calls():
    h = html2text.HTML2Text()
    md1 = h.handle("<p>test</test>")
    md2 = h.handle("<p>test</test>")
    assert md1 == md2
