import html2text

def test_emphasis_with_new_line():
    h = html2text.HTML2Text()
    html = "<b>Our multiline<br />bold text</b>"
    result = h.handle(html)
    assert result == '**Our multiline**  \n**bold text**\n\n'
    