import pytest

try:
    import app
except ModuleNotFoundError:
    pytest.skip("nltk not installed", allow_module_level=True)


def test_single_word_translation():
    result = app.translate_text("dog")
    assert result.strip() == "u'i gerku"


def test_multi_word_translation():
    result = app.translate_text("man love")
    assert result.strip() == "u'i lo nanmu cu prami"


def test_phrase_translation():
    result = app.translate_text("ice cream")
    assert result.strip() == "u'i bisyladru"
