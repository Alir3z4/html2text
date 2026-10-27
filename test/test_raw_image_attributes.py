import subprocess
import sys
from html.parser import HTMLParser

import pytest

from html2text import HTML2Text


class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(attrs)


@pytest.mark.parametrize("option", ["images_as_html", "images_with_size"])
@pytest.mark.parametrize("surface", ["module", "command"])
@pytest.mark.parametrize(
    "source,default_alt,expected",
    [
        (
            '<img src="/O&#x27;Reilly" alt="Tom&#x27;s &quot;&lt;&amp;&gt; café" '
            'width="12&#x27;3" height="4&amp;5" discarded="no">',
            "",
            {
                "src": "/O'Reilly",
                "alt": "Tom's \"<&> café",
                "width": "12'3",
                "height": "4&5",
            },
        ),
        (
            '<img src="/&amp;copy;" alt="&amp;copy;" '
            'width="&amp;copy;" height="&amp;copy;">',
            "",
            {
                "src": "/&copy;",
                "alt": "&copy;",
                "width": "&copy;",
                "height": "&copy;",
            },
        ),
        (
            '<img src="x" width="12" height="4">',
            "",
            {"src": "x", "width": "12", "height": "4"},
        ),
        (
            '<img src="x" width="12" alt>',
            "O'Reilly &copy;",
            {"src": "x", "width": "12", "alt": "O'Reilly &copy;"},
        ),
    ],
    ids=["quoted", "literal_entity", "plain", "default_alt"],
)
def test_raw_image_attributes(option, surface, source, default_alt, expected):
    if surface == "command":
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "html2text",
                "--" + option.replace("_", "-"),
                "--body-width=0",
                "--default-image-alt=" + default_alt,
            ],
            input=source,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout
    else:
        converter = HTML2Text(bodywidth=0)
        setattr(converter, option, True)
        converter.default_image_alt = default_alt
        result = converter.handle(source)
    parser = ImageParser()
    parser.feed(result)
    assert [dict(attrs) for attrs in parser.images] == [expected]
    assert len(parser.images[0]) == len(expected)
