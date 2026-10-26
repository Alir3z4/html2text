from typing import Dict, Optional

import pytest

import html2text


@pytest.mark.parametrize(
    "html, expected",
    [
        ("<option>abc</option><option>def</option>", "abc def\n"),
        ("<select><option>abc</option><option>def</option></select>", "abc def\n"),
        ("<select><option>abc<option>def</select>", "abc def\n"),
        ("<option>abc</option> <option>def</option>", "abc def\n"),
        ("<option>abc </option><option>def</option>", "abc def\n"),
        ("<option>abc</option><option> def</option>", "abc def\n"),
        ("<option>abc\n</option><option>def</option>", "abc def\n"),
        ("<option>a&nbsp;</option><option>b</option>", "a b\n"),
        ("<option>a</option><option>&nbsp;b</option>", "a b\n"),
        ("<option><code>a </code></option><option>b</option>", "`a ` b\n"),
        ("<option>abc</option>", "abc\n"),
        ("<option></option><option>def</option>", "def\n"),
        ("<option>abc</option><option></option>", "abc\n"),
        ("<option>A &amp; B</option><option>C</option>", "A & B C\n"),
        (
            '<select><optgroup label="one"><option>A</option></optgroup>'
            '<optgroup label="two"><option>B</option></optgroup></select>',
            "A B\n",
        ),
        ("<option><b>abc</b></option><option>def</option>", "**abc** def\n"),
        ("<option><code>abc</code></option><option>def</option>", "`abc` def\n"),
        ("<code>&lt;option&gt;abc&lt;/option&gt;</code>", "`<option>abc</option>`\n"),
        (
            "<pre>&lt;option&gt;abc&lt;/option&gt;</pre>",
            "\n    <option>abc</option>\n",
        ),
        ("<code><option>abc</option><option>def</option></code>", "`abcdef`\n"),
        ("<pre><option>abc</option><option>def</option></pre>", "\n    abcdef\n"),
        ("a<head><option>hidden</option></head>b", "ab\n"),
    ],
)
def test_option_spacing(html: str, expected: str) -> None:
    assert html2text.HTML2Text(bodywidth=0).handle(html) == expected


def test_option_spacing_wrapping() -> None:
    converter = html2text.HTML2Text(bodywidth=10)
    html = (
        "<select><option>alpha</option><option>beta</option>"
        "<option>gamma</option></select>"
    )
    assert converter.handle(html) == "alpha beta\ngamma\n\n"


def test_option_tag_callback_can_skip_spacing() -> None:
    def skip_options(
        converter: html2text.HTML2Text,
        tag: str,
        attrs: Dict[str, Optional[str]],
        start: bool,
    ) -> Optional[bool]:
        if tag == "option":
            return True
        return None

    converter = html2text.HTML2Text()
    converter.tag_callback = skip_options
    assert converter.handle("<option>abc</option><option>def</option>") == "abcdef\n\n"


def test_option_spacing_custom_output() -> None:
    output = []
    converter = html2text.HTML2Text(out=output.append, bodywidth=0)
    converter.handle("<option>abc</option><option>def</option>")
    assert "".join(output) == "abc def\n"


@pytest.mark.parametrize("entity", ["&nbsp;", "&#160;", "&#xA0;"])
@pytest.mark.parametrize("trailing", [False, True])
def test_option_spacing_nonbreaking_space(entity: str, trailing: bool) -> None:
    converter = html2text.HTML2Text(bodywidth=0)
    converter.unicode_snob = True
    if trailing:
        source = f"<option>a{entity}</option><option>b</option>"
    else:
        source = f"<option>a</option><option>{entity}b</option>"
    separator = "\N{NO-BREAK SPACE}" if entity == "&nbsp;" else " "
    assert converter.handle(source) == f"a{separator}b\n"


@pytest.mark.parametrize("tag", ["em", "i", "u"])
@pytest.mark.parametrize("first_label", ["a", "a ", "a&nbsp;"])
def test_option_spacing_before_emphasis(tag: str, first_label: str) -> None:
    source = f"<option>{first_label}</option><option><{tag}>b</{tag}></option>"
    assert html2text.HTML2Text(bodywidth=0).handle(source) == "a _b_\n"
