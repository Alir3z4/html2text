import html2text

# See https://github.com/Alir3z4/html2text/issues/163 for more information.


def test_newline_on_multiple_calls():
    h = html2text.HTML2Text()
    html = "<p>test</p>"
    md1 = h.handle(html)
    md2 = h.handle(html)
    md3 = h.handle(html)
    assert md1 == md2 == md3


def test_abbreviations_do_not_leak_between_documents():
    h = html2text.HTML2Text()
    first = h.handle('<abbr title="First">A</abbr>')
    second = h.handle('<abbr title="Second">B</abbr>')
    third = h.handle("<p>Next</p>")
    assert "*[A]: First" in first
    assert "*[B]: Second" in second
    assert "*[A]: First" not in second
    assert "*[A]: First" not in third
    assert "*[B]: Second" not in third


def test_abbreviations_are_kept_until_finish():
    h = html2text.HTML2Text()
    h.feed('<abbr title="First">A</abbr> and ')
    h.feed('<abbr title="Second">B</abbr>')
    first = h.finish()
    assert "*[A]: First" in first
    assert "*[B]: Second" in first
    h.feed("<p>Next</p>")
    second = h.finish()
    assert "*[A]: First" not in second
    assert "*[B]: Second" not in second
