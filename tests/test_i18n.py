"""Tests for the i18n helper."""

from bot.i18n import DEFAULT_LANG, LANGUAGES, t


def test_t_returns_localized_string():
    assert t("ru", "lang.changed") == "✅ Язык изменён на русский."
    assert t("en", "lang.changed") == "✅ Language switched to English."


def test_t_falls_back_to_default_lang_for_unknown_lang():
    assert t("zz", "menu.btn.profile") == t(DEFAULT_LANG, "menu.btn.profile")


def test_t_returns_key_for_unknown_key():
    assert t("ru", "totally.made.up.key") == "totally.made.up.key"


def test_t_formats_kwargs():
    out = t("en", "product.price", price=42)
    assert "42" in out


def test_languages_keys_match_translation_subkeys():
    """Every LANGUAGES code should have a translation in every key (sanity check)."""
    from bot.i18n import TRANSLATIONS

    missing = []
    for key, entry in TRANSLATIONS.items():
        for code in LANGUAGES:
            if code not in entry:
                missing.append(f"{key}:{code}")
    assert not missing, f"Missing translations: {missing}"
