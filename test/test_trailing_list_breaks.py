import pytest

import html2text


@pytest.mark.parametrize("tag", ["ul", "ol"])
@pytest.mark.parametrize("width", [0, 78])
@pytest.mark.parametrize("breaks", ["<br />", "<br><br>", "<br> \n<!-- tail -->"])
def test_trailing_breaks_do_not_make_a_list_loose(tag, width, breaks):
    source = "<{0}><li>Item 1 {1}</li><li>Item 2</li></{0}>"
    assert html2text.html2text(source.format(tag, breaks), bodywidth=width) == (
        html2text.html2text(source.format(tag, ""), bodywidth=width)
    )


@pytest.mark.parametrize(
    "content",
    [
        "<strong>First<br></strong>",
        "<em>First<br></em>",
        '<a href="https://example.com">First<br></a>',
        "<span>First<br></span>",
    ],
)
def test_closing_inline_tags_do_not_flush_a_trailing_break(content):
    source = "<ul><li>" + content + "</li><li>Second</li></ul>"
    assert html2text.html2text(source) == html2text.html2text(
        source.replace("<br>", "")
    )


@pytest.mark.parametrize("breaks", ["<br>", "<br><br>"])
@pytest.mark.parametrize("following", ["Second", "<strong>Second</strong>"])
def test_breaks_between_list_content_are_preserved(breaks, following):
    source = "<ul><li>First" + breaks + following + "</li></ul>"
    result = html2text.html2text(source, bodywidth=0)
    assert "First" + "  \n" * breaks.count("<br>") in result
    assert "Second" in result


def test_break_before_a_nested_list_does_not_add_an_empty_line():
    source = "<ul><li>Parent<br><ol><li>Child<br></li></ol></li><li>Next</li></ul>"
    assert html2text.html2text(source) == html2text.html2text(
        source.replace("<br>", "")
    )


def test_paragraph_separation_is_preserved():
    result = html2text.html2text(
        "<ul><li><p>First</p><p>Second</p></li></ul>", bodywidth=0
    )
    assert "First\n\nSecond" in result


def test_breaks_outside_lists_and_inside_preformatted_text_are_preserved():
    assert html2text.html2text("First<br>Second", bodywidth=0) == "First  \nSecond\n"
    result = html2text.html2text(
        "<ul><li><pre>First<br>Second</pre></li></ul>", bodywidth=0
    )
    assert "First  \n" in result
    assert "Second" in result


def test_chunked_input_with_custom_output_ignores_only_the_trailing_break():
    source = "<ul><li>First<br>Second<br></li><li>Third</li></ul>"
    output = []
    converter = html2text.HTML2Text(out=output.append, bodywidth=0)
    for character in source:
        converter.feed(character)
    converter.finish()
    result = "".join(output)
    assert "First  \nSecond\n" in result
    assert "Second  \n" not in result


def test_ignored_content_does_not_flush_the_trailing_break():
    source = '<ul><li>First<br><script>ignored()</script><img src="ignored"></li></ul>'
    converter = html2text.HTML2Text()
    converter.ignore_images = True
    assert converter.handle(source) == html2text.html2text("<ul><li>First</li></ul>")


def test_unclosed_list_at_eof_does_not_leak_a_break_to_the_next_document():
    converter = html2text.HTML2Text(bodywidth=0)
    first = converter.handle("<ul><li>First<br>")
    assert first == "  * First\n"
    assert converter.handle("Second") == "Second\n"
