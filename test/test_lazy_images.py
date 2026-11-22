import pytest

from html2text import HTML2Text


@pytest.mark.parametrize("src", ["", " src", ' src=""'])
@pytest.mark.parametrize(
    "options, expected",
    [
        ({}, "![photo](picture.jpg)"),
        ({"images_as_html": True}, "<img src='picture.jpg' alt='photo' />"),
        ({"images_to_alt": True}, "photo"),
        ({"ignore_images": True}, ""),
        ({"inline_links": False}, "![photo][1]\n\n   [1]: picture.jpg"),
    ],
)
def test_lazy_image(src, options, expected):
    parser = HTML2Text(bodywidth=0)
    for name, value in options.items():
        setattr(parser, name, value)
    result = parser.handle(f'<img{src} data-src="picture.jpg" alt="photo">')
    assert result.strip() == expected


def test_lazy_image_with_size_and_base_url():
    parser = HTML2Text(baseurl="https://example.com/", bodywidth=0)
    assert parser.handle('<img data-src="picture.jpg">').strip() == (
        "![](https://example.com/picture.jpg)"
    )
    parser = HTML2Text(bodywidth=0)
    parser.images_with_size = True
    assert parser.handle('<img data-src="picture.jpg" width="10">').strip() == (
        "<img src='picture.jpg' width='10' />"
    )


def test_explicit_src_takes_precedence():
    parser = HTML2Text(bodywidth=0)
    assert parser.handle('<img src="primary.jpg" data-src="lazy.jpg">').strip() == (
        "![](primary.jpg)"
    )


@pytest.mark.parametrize("attribute", ["data-src", 'data-src=""'])
def test_empty_lazy_src(attribute):
    parser = HTML2Text(bodywidth=0)
    assert parser.handle(f"before <img {attribute}> after").strip() == "before  after"
