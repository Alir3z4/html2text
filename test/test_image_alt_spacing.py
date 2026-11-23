import pytest

from html2text import HTML2Text


@pytest.mark.parametrize(
    "html, expected",
    [
        ('<img alt="hello" src="image.png">world', "hello world"),
        ('<img alt="hello" src="image.png"> world', "hello world"),
        ('<img alt="hello " src="image.png">world', "hello world"),
        ('<img alt="hello" src="image.png">, world!', "hello, world!"),
        ('<img alt="hello" src="image.png">&amp; world', "hello & world"),
        ('<img alt="hello" src="image.png"><span>world</span>', "hello world"),
        ('<img alt="hello" src="image.png"><strong>world</strong>', "hello **world**"),
        ('<img alt="hello" src="image.png"><em>world</em>', "hello _world_"),
        ('<img alt="hello" src="image.png"><code>world</code>', "hello `world`"),
        ('<img alt="hello" src="image.png">&nbsp;world', "hello world"),
        ('<strong><img alt="hello" src="image.png"> world</strong>', "**hello world**"),
        ('<strong><img alt="hello" src="image.png"></strong>world', "**hello** world"),
        ('<code><img alt="hello" src="image.png">world</code>', "`helloworld`"),
        (
            '<img alt="hello" src="image.png"><a href="/next">world</a>',
            "hello [world](/next)",
        ),
        (
            '<a href="/next"><img alt="hello" src="image.png"></a>world',
            "[hello](/next) world",
        ),
        (
            '<img alt="hello" src="image.png"><img alt="world" src="other.png">',
            "hello world",
        ),
        (
            '<img alt="hello" src="image.png"><img alt="" src="other.png">world',
            "hello world",
        ),
        ('<img alt="" src="image.png">world', "world"),
        ('<img alt="hello" src="image.png"><p>world</p>', "hello\n\nworld"),
        (
            '<img alt="hello" src="image.png"><script>ignored</script>world',
            "hello world",
        ),
        (
            '<a href="https://example.com">'
            '<img alt="https://example.com" src="image.png"></a>world',
            "<https://example.com> world",
        ),
    ],
)
def test_alt_text_has_a_boundary_before_following_words(html, expected):
    converter = HTML2Text(bodywidth=0)
    converter.images_to_alt = True
    assert converter.handle(html).strip() == expected


def test_alt_boundary_does_not_leak_to_the_next_document():
    converter = HTML2Text(bodywidth=0)
    converter.images_to_alt = True
    assert converter.handle('<img alt="hello" src="image.png">').strip() == "hello"
    assert converter.handle("world").strip() == "world"


def test_normal_markdown_images_keep_the_existing_output():
    converter = HTML2Text(bodywidth=0)
    assert (
        converter.handle('<img alt="hello" src="image.png">world').strip()
        == "![hello](image.png)world"
    )


def test_alt_boundary_works_with_streaming_and_custom_output():
    chunks = []
    converter = HTML2Text(out=chunks.append, bodywidth=0)
    converter.images_to_alt = True
    converter.feed('<img alt="hello" src="image.png">')
    converter.feed("world")
    converter.finish()
    assert "".join(chunks).strip() == "hello world"
