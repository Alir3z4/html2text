import pytest

from html2text import HTML2Text

TABLE = (
    "<table><tbody><tr><td>item a</td><td>item b</td></tr>"
    "<tr><td>item c</td><td>item d</td></tr></tbody></table>"
)
EXPECTED = "|  |  |\n| --- | --- |\nitem a| item b\nitem c| item d"


def lines(text):
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def test_first_data_row_is_not_promoted_to_a_header():
    assert lines(HTML2Text(bodywidth=0).handle(TABLE)) == EXPECTED


@pytest.mark.parametrize("chunk_size", [1, 7, 1000])
def test_streaming_output_receives_the_header_before_any_data(chunk_size):
    output = []
    parser = HTML2Text(out=output.append, bodywidth=0)
    for offset in range(0, len(TABLE), chunk_size):
        parser.feed(TABLE[offset : offset + chunk_size])
    parser.finish()
    assert lines("".join(output)) == EXPECTED


@pytest.mark.parametrize(
    "header", ["<th>Name</th><td>Value</td>", "<td>Name</td><th>Value</th>"]
)
def test_a_th_anywhere_in_the_first_row_keeps_that_row_as_the_header(header):
    text = HTML2Text(bodywidth=0).handle("<table><tr>" + header + "</tr></table>")
    assert lines(text) == "Name| Value\n---|---"


def test_explicit_thead_is_a_header_even_with_td_cells():
    text = HTML2Text(bodywidth=0).handle(
        "<table><thead><tr><td>Name</td><td>Value</td></tr></thead></table>"
    )
    assert lines(text) == "Name| Value\n---|---"


def test_cell_formatting_and_links_are_preserved():
    parser = HTML2Text(bodywidth=0)
    text = parser.handle(
        "<p>Before</p><table><tr><td><em>A</em></td>"
        '<td><a href="https://example.com">B</a></td></tr></table><p>After</p>'
    )
    assert lines(text) == (
        "Before\n\n|  |  |\n| --- | --- |\n _A_| [B](https://example.com)\n\nAfter"
    )


def test_single_column_has_an_unambiguous_table_delimiter():
    text = HTML2Text(bodywidth=0).handle("<table><tr><td>A</td></tr></table>")
    assert lines(text) == "|  |\n| --- |\nA"


def test_padding_keeps_the_first_data_row_below_the_separator():
    parser = HTML2Text(bodywidth=0)
    parser.pad_tables = True
    text = parser.handle(TABLE)
    rows = [row.strip() for row in text.splitlines() if row.strip()]
    assert rows[0].replace(" ", "") == "|||"
    assert rows[1].replace("-", "") == "|||"
    assert "item a" in rows[2] and "item c" in rows[3]


@pytest.mark.parametrize("html", [TABLE, TABLE.replace("</tr>", ""), TABLE[:-16]])
def test_unclosed_rows_and_finish_flush_first_row_buffers(html):
    parser = HTML2Text(bodywidth=0)
    text = parser.handle(html)
    assert "item a" in text
    assert lines(text).startswith("|  |  |\n| --- | --- |\nitem a| item b")
    assert lines(parser.handle(TABLE)) == EXPECTED


def test_multiple_tables_get_independent_headers():
    text = HTML2Text(bodywidth=0).handle(TABLE + TABLE)
    assert lines(text).count("|  |  |\n| --- | --- |") == 2


def test_finish_flushes_an_unclosed_first_row():
    parser = HTML2Text(bodywidth=0)
    assert lines(parser.handle("<table><tr><td>A")) == "|  |\n| --- |\nA"
    assert lines(parser.handle(TABLE)) == EXPECTED


def test_empty_first_row_does_not_consume_the_header():
    text = HTML2Text(bodywidth=0).handle(TABLE.replace("<tbody>", "<tbody><tr></tr>"))
    assert lines(text) == EXPECTED


def test_table_in_a_blockquote_keeps_its_indentation():
    text = HTML2Text(bodywidth=0).handle("<blockquote>" + TABLE + "</blockquote>")
    assert lines(text) == "\n".join("> " + row for row in EXPECTED.splitlines())


@pytest.mark.parametrize("html", ["<table></table>", "<table><tr></tr></table>"])
def test_empty_tables_do_not_gain_header_cells(html):
    assert "|" not in HTML2Text(bodywidth=0).handle(html)


@pytest.mark.parametrize("mode", ["ignore_tables", "bypass_tables"])
def test_raw_and_ignored_tables_do_not_gain_markdown_headers(mode):
    parser = HTML2Text(bodywidth=0)
    setattr(parser, mode, True)
    assert "| --- |" not in parser.handle(TABLE)
