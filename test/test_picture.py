import pytest

from html2text import HTML2Text


@pytest.mark.parametrize("attribute", ["", 'src=""', "src"])
def test_picture_uses_first_source_when_img_has_no_url(attribute):
    html = (
        '<picture><source srcset=" small.png 640w, large.png 1280w">'
        '<source srcset="other.png 1x"><img alt="Photo" ' + attribute + "></picture>"
    )
    assert HTML2Text(bodywidth=0).handle(html).strip() == "![Photo](small.png)"


def test_explicit_img_src_wins_without_duplicate_images():
    html = (
        '<picture><source srcset="other.png 2x">'
        '<img src="fallback.png" alt="A"></picture>'
    )
    assert HTML2Text(bodywidth=0).handle(html).strip() == "![A](fallback.png)"


def test_picture_context_does_not_leak():
    parser = HTML2Text(bodywidth=0)
    html = (
        '<picture><source srcset="one.png"><img></picture>'
        '<img><source srcset="two.png">'
    )
    assert parser.handle(html).strip() == "![](one.png)"
    parser.handle('<picture><source srcset="unfinished.png">')
    assert parser.handle("<img>").strip() == ""


def test_picture_ignores_empty_sources_and_keeps_commas_in_urls():
    html = (
        '<picture><source srcset><source srcset=" ,  ">'
        '<source srcset="a,b.png 1x, other.png 2x"><img></picture>'
    )
    assert HTML2Text(bodywidth=0).handle(html).strip() == "![](a,b.png)"


@pytest.mark.parametrize(
    "option, expected",
    [
        ("ignore_images", ""),
        ("images_to_alt", "Photo"),
        ("images_as_html", "<img src='small.png' alt='Photo' />"),
    ],
)
def test_picture_respects_image_options(option, expected):
    parser = HTML2Text(bodywidth=0)
    setattr(parser, option, True)
    html = '<picture><source srcset="small.png"><img alt="Photo"></picture>'
    assert parser.handle(html).strip() == expected


def test_picture_reference_links_and_base_url():
    parser = HTML2Text(baseurl="https://example.com/folder/", bodywidth=0)
    parser.inline_links = False
    result = parser.handle(
        '<picture><source srcset="small.png"><img alt="Photo"></picture>'
    )
    assert "![Photo][1]" in result
    assert "[1]: https://example.com/folder/small.png" in result


def test_picture_source_works_with_incremental_feed():
    parser = HTML2Text(bodywidth=0)
    parser.feed('<picture><source srcset="small.png')
    parser.feed(' 1x"><img alt="Photo"></picture>')
    assert parser.finish().strip() == "![Photo](small.png)"
