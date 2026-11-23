import pytest

import html2text


def table_rows(markdown):
    rows = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        rows.append([cell.strip() for cell in line.split("|")])
    return rows


@pytest.mark.parametrize("pad", [False, True])
@pytest.mark.parametrize("tag", ["th", "td"])
def test_colspan_keeps_following_columns_aligned(pad, tag):
    converter = html2text.HTML2Text(bodywidth=0)
    converter.pad_tables = pad
    source = (
        '<table><tr><{0} colspan="2">A</{0}><{0}>B</{0}></tr>'
        "<tr><td>1</td><td>2</td><td>3</td></tr></table>"
    ).format(tag)
    rows = table_rows(converter.handle(source))
    assert rows[0] == ["A", "", "B"]
    assert len(rows[1]) == 3
    assert all(set(cell) == {"-"} for cell in rows[1])
    assert rows[2] == ["1", "2", "3"]


@pytest.mark.parametrize("pad", [False, True])
def test_spanning_last_cell_has_trailing_empty_columns(pad):
    converter = html2text.HTML2Text(bodywidth=0)
    converter.pad_tables = pad
    rows = table_rows(
        converter.handle(
            '<table><tr><th colspan="3">All</th></tr>'
            '<tr><td>A</td><td colspan="2">B</td></tr>'
            '<tr><td colspan="3">C</td></tr></table>'
        )
    )
    assert rows[0] == ["All", "", ""]
    assert len(rows[1]) == 3
    assert rows[2:] == [["A", "B", ""], ["C", "", ""]]


@pytest.mark.parametrize("pad", [False, True])
def test_empty_spanning_first_cell_is_preserved(pad):
    converter = html2text.HTML2Text(bodywidth=0)
    converter.pad_tables = pad
    rows = table_rows(
        converter.handle('<table><tr><th colspan="2"></th><th>B</th></tr></table>')
    )
    assert rows[0] == ["", "", "B"]
    assert len(rows[1]) == 3


@pytest.mark.parametrize("span", ["", "0", "-2", "two", "2.5"])
def test_invalid_spans_fall_back_to_one_column(span):
    source = '<table><tr><th colspan="{}">A</th><th>B</th></tr></table>'
    assert html2text.html2text(source.format(span)) == html2text.html2text(
        source.format("1")
    )


def test_colspan_is_bounded_by_the_html_limit():
    converter = html2text.HTML2Text(bodywidth=0)
    rows = table_rows(
        converter.handle('<table><tr><th colspan="999999999">A</th></tr></table>')
    )
    assert len(rows[0]) == 1000
    assert len(rows[1]) == 1000


@pytest.mark.parametrize("option", ["ignore_tables", "bypass_tables"])
def test_non_markdown_table_modes_do_not_expand_colspans(option):
    source = "<table><tr><th{}>A</th><th>B</th></tr></table>"
    converter = html2text.HTML2Text(bodywidth=0)
    setattr(converter, option, True)
    assert converter.handle(source.format(' colspan="2"')) == converter.handle(
        source.format("")
    )


def test_chunked_input_and_output_callback_keep_spanning_cells():
    source = (
        '<table><tr><th colspan="2">A</th><th>B</th></tr>'
        "<tr><td>1</td><td>2</td><td>3</td></tr></table>"
    )
    chunks = []
    converter = html2text.HTML2Text(out=chunks.append, bodywidth=0)
    for character in source:
        converter.feed(character)
    converter.finish()
    assert table_rows("".join(chunks))[0] == ["A", "", "B"]


def test_colspan_does_not_leak_to_following_rows_or_tables():
    converter = html2text.HTML2Text(bodywidth=0)
    converter.handle('<table><tr><th colspan="3">A</th></tr></table>')
    source = "<table><tr><th>A</th><th>B</th></tr></table>"
    assert converter.handle(source) == html2text.html2text(source, bodywidth=0)


def test_omitted_cell_end_tags_do_not_drop_placeholders():
    converter = html2text.HTML2Text(bodywidth=0)
    rows = table_rows(
        converter.handle('<table><tr><th colspan="2">A<th>B</tr></table>')
    )
    assert rows[0] == ["A", "", "B"]
    assert len(rows[1]) == 3
