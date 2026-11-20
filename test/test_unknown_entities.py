import pytest

from html2text import HTML2Text


@pytest.mark.parametrize("unicode_snob", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "Sample text K&N. Sample text.",
        "&unknown; &unknown. &unknown=1",
        "https://example.com/?a=1&code=abc",
        "&unknown &unknown; &unknown",
    ],
)
def test_unknown_entities_keep_their_original_semicolons(text, unicode_snob):
    parser = HTML2Text(bodywidth=0)
    parser.unicode_snob = unicode_snob
    assert parser.handle("<p>" + text + "</p>").strip() == text


STREAMING_SOURCE = (
    '<p title="&unknown;"><!-- &unknown; -->&unknown;\n'
    "first &unknown.</p><p>&unknown=1</p>"
)


@pytest.mark.parametrize("split", range(len(STREAMING_SOURCE) + 1))
def test_unknown_entities_across_feed_boundaries(split):
    parser = HTML2Text(bodywidth=0)
    parser.feed(STREAMING_SOURCE[:split])
    parser.feed(STREAMING_SOURCE[split:])
    assert parser.finish().strip() == "&unknown; first &unknown.\n\n&unknown=1"


def test_unknown_entities_one_character_at_a_time():
    parser = HTML2Text(bodywidth=0)
    for character in "<p>&unknown; &unknown=1 &amp; &copy;</p>":
        parser.feed(character)
    assert parser.finish().strip() == "&unknown; &unknown=1 & (C)"


def test_known_entities_and_custom_replacements_are_preserved():
    parser = HTML2Text(bodywidth=0)
    assert parser.handle("<p>&amp; &copy; &nbsp; &lrm;</p>").strip() == "& (C)"
    parser.unicode_snob = True
    assert parser.handle("<p>&copy;</p>").strip() == "\N{COPYRIGHT SIGN}"
