import pytest

from html2text import HTML2Text


@pytest.mark.parametrize(
    "prefix",
    [
        "old",
        "<blockquote><ol start='7'><li><em>old",
        "<pre>old",
        "<code>old",
        "<q>old",
        "<a href='/old'>old",
        "<table><tr><td>old",
        "<abbr title='old definition'>old",
        "<head>old",
        "<style>p {color: red}</style><p>old",
    ],
)
def test_failed_handle_does_not_contaminate_the_next_document(prefix):
    parser = HTML2Text(bodywidth=0)
    error = AssertionError("formatter failed")

    def fail_on_tag(converter, tag, attrs, start):
        if tag == "fail":
            raise error

    # A callback makes the failure deterministic on Python versions where the
    # standard HTMLParser now accepts the malformed declaration from #400.
    parser.tag_callback = fail_on_tag
    with pytest.raises(AssertionError) as caught:
        parser.handle(prefix + "<fail>")
    assert caught.value is error
    assert parser.handle("<p>Goodbye</p>") == "Goodbye\n"
    assert parser.tag_callback is fail_on_tag


def test_recovery_preserves_configuration_and_subclass_state():
    class Converter(HTML2Text):
        def __init__(self):
            super().__init__(baseurl="https://example.com/", bodywidth=0)
            self.initializations = getattr(self, "initializations", 0) + 1
            self.emphasis_mark = "*"
            self.ul_item_mark = "+"
            self.inline_links = False
            self.custom_state = object()

    parser = Converter()
    custom_state = parser.custom_state

    def fail_on_tag(converter, tag, attrs, start):
        if tag == "fail":
            raise RuntimeError("callback failed")

    parser.tag_callback = fail_on_tag
    with pytest.raises(RuntimeError, match="callback failed"):
        parser.handle('<a href="/old">old</a><ul><li><fail>')
    html = '<p><em>fresh</em> <a href="/new">link</a></p><ul><li>item</li></ul>'
    assert parser.handle(html) == Converter().handle(html)
    assert parser.initializations == 1
    assert parser.custom_state is custom_state
    assert parser.tag_callback is fail_on_tag


def test_output_callback_is_retained_after_it_raises():
    chunks = []

    def output(text):
        if text == "broken":
            raise ValueError("output failed")
        chunks.append(text)

    parser = HTML2Text(out=output, bodywidth=0)
    with pytest.raises(ValueError, match="output failed"):
        parser.handle("<blockquote>broken</blockquote>")
    # Output already delivered to the caller cannot be retracted.
    chunks.clear()
    parser.handle("Goodbye")
    assert "".join(chunks) == "Goodbye\n"
    assert parser.out is output
