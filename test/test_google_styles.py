import pytest

from html2text import HTML2Text


@pytest.mark.parametrize("attributes", ["class", "style", "class style"])
@pytest.mark.parametrize(
    "parent_style", ["", "font-weight: bold", "font-style: italic"]
)
def test_google_doc_attributes_without_values(attributes, parent_style):
    def convert(attributes):
        converter = HTML2Text()
        converter.google_doc = True
        return converter.handle(
            '<p style="{}"><span {}>Hello</span></p>'.format(parent_style, attributes)
        )

    assert convert(attributes) == convert("")
