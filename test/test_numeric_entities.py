import pytest

import html2text


@pytest.mark.parametrize(
    "entity, expected",
    [
        pytest.param("9" * 5000, "\ufffd", id="oversized-decimal"),
        pytest.param("x" + "f" * 5000, "\ufffd", id="oversized-hex"),
        pytest.param("0" * 5000 + "65", "A", id="decimal-leading-zeros"),
        pytest.param("X" + "0" * 5000 + "41", "A", id="hex-leading-zeros"),
        pytest.param("0" * 5000, "\ufffd", id="zero"),
        pytest.param("1114112", "\ufffd", id="above-unicode-range"),
        pytest.param("xD800", "\ufffd", id="surrogate"),
        pytest.param("128", "\u20ac", id="windows-1252-replacement"),
    ],
)
@pytest.mark.parametrize("unicode_snob", [False, True])
def test_numeric_entities(entity, expected, unicode_snob):
    converter = html2text.HTML2Text()
    converter.unicode_snob = unicode_snob

    assert converter.handle("before &#" + entity + "; after") == (
        "before " + expected + " after\n\n"
    )
