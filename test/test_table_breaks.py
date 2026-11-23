import pytest

import html2text


@pytest.mark.parametrize("pad", [False, True])
@pytest.mark.parametrize("width", [0, 78])
def test_breaks_keep_header_and_data_cells_on_one_markdown_row(pad, width):
    converter = html2text.HTML2Text(bodywidth=width)
    converter.pad_tables = pad
    result = converter.handle(
        "<table><tr><th>Minimum<br>Maximum</th><th>Name</th></tr>"
        "<tr><td>0<br />1</td><td>Value</td></tr></table>"
    )
    lines = [line.strip().strip("|").strip() for line in result.splitlines()]
    rows = [[cell.strip() for cell in line.split("|")] for line in lines if line]
    assert len(rows) == 3
    assert rows[0] == ["Minimum<br>Maximum", "Name"]
    assert len(rows[1]) == 2
    assert all(set(cell) == {"-"} for cell in rows[1])
    assert rows[2] == ["0<br>1", "Value"]


@pytest.mark.parametrize(
    "content, expected",
    [
        ("<br>First<br><br>Last<br>", "<br>First<br><br>Last<br>"),
        ("<strong>First<br>Last</strong>", "**First<br> Last**"),
        ("<code>First<br>Last</code>", "`First`<br>`Last`"),
        ("<span>First</span><br><em>Last</em>", "First<br> _Last_"),
    ],
)
def test_breaks_preserve_inline_content(content, expected):
    result = html2text.html2text(
        "<table><tr><td>" + content + "</td><td>Other</td></tr></table>",
        bodywidth=0,
    )
    assert [cell.strip() for cell in result.splitlines()[0].split("|")] == [
        expected,
        "Other",
    ]


@pytest.mark.parametrize("mode", ["ignore_tables", "bypass_tables"])
def test_existing_non_markdown_table_modes_keep_hard_breaks(mode):
    converter = html2text.HTML2Text(bodywidth=0)
    setattr(converter, mode, True)
    result = converter.handle("<table><tr><td>First<br>Last</td></tr></table>")
    assert "First  \nLast" in result
    assert "<br>" not in result


def test_breaks_outside_cells_keep_their_normal_behavior():
    result = html2text.html2text(
        "<p>Before<br>table</p><table><tr><td>Inside<br>cell</td></tr></table>"
        "<p>After<br>table</p><blockquote>Quoted<br>text</blockquote>",
        bodywidth=0,
    )
    assert "Before  \ntable" in result
    assert "Inside<br>cell" in result
    assert "After  \ntable" in result
    assert "> Quoted  \n> text" in result


def test_omitted_cell_end_tag_stops_at_row_boundary():
    result = html2text.html2text(
        "<table><tr><td>Inside<br>cell</tr></table>Outside<br>table", bodywidth=0
    )
    assert "Inside<br>cell" in result
    assert "Outside  \ntable" in result


def test_chunked_input_and_custom_output_keep_table_breaks_inline():
    output = []
    converter = html2text.HTML2Text(out=output.append, bodywidth=0)
    for character in "<table><tr><th>First<br>Last</th></tr></table>":
        converter.feed(character)
    converter.finish()
    assert "".join(output).splitlines()[0] == "First<br>Last  "


def test_reusing_converter_does_not_leak_table_context():
    converter = html2text.HTML2Text(bodywidth=0)
    converter.handle("<table><tr><td>A<br>B</td></tr></table>")
    assert converter.handle("C<br>D") == "C  \nD\n"
