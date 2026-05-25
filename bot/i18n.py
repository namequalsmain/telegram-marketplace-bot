"""Simple dict-based i18n.

Adding a new language:
  1. Add it to LANGUAGES below
  2. Add the language code as a sub-key in every entry of TRANSLATIONS
"""

DEFAULT_LANG = "ru"

LANGUAGES: dict[str, str] = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── language picker ─────────────────────────────────────────────────────
    "lang.pick": {
        "ru": "🌐 Выберите язык / Choose your language:",
        "en": "🌐 Choose your language / Выберите язык:",
    },
    "lang.changed": {
        "ru": "✅ Язык изменён на русский.",
        "en": "✅ Language switched to English.",
    },

    # ── main menu ──────────────────────────────────────────────────────────
    "menu.greeting": {
        "ru": "👋 Привет, <b>{name}</b>!\n\nДобро пожаловать в магазин. Выбирай раздел ниже.",
        "en": "👋 Hi, <b>{name}</b>!\n\nWelcome to the shop. Pick a section below.",
    },
    "menu.btn.profile":  {"ru": "👤 Профиль",         "en": "👤 Profile"},
    "menu.btn.catalog":  {"ru": "🛒 Товары",          "en": "🛒 Products"},
    "menu.btn.support":  {"ru": "🆘 Тех. поддержка",  "en": "🆘 Support"},
    "menu.btn.tos":      {"ru": "📄 Соглашение",       "en": "📄 Terms"},
    "menu.btn.settings": {"ru": "⚙️ Настройки",       "en": "⚙️ Settings"},
    "menu.btn.back":     {"ru": "« В меню",            "en": "« Menu"},

    # ── profile ────────────────────────────────────────────────────────────
    "profile.text": {
        "ru": (
            "<b>👤 Профиль</b>\n\n"
            "ID: <code>{id}</code>\n"
            "Username: @{username}\n"
            "Баланс: <b>{balance}</b> ⭐\n"
            "Зарегистрирован: {reg_date}"
        ),
        "en": (
            "<b>👤 Profile</b>\n\n"
            "ID: <code>{id}</code>\n"
            "Username: @{username}\n"
            "Balance: <b>{balance}</b> ⭐\n"
            "Registered: {reg_date}"
        ),
    },

    # ── ToS / support ──────────────────────────────────────────────────────
    "tos.title":     {"ru": "<b>📄 Пользовательское соглашение</b>", "en": "<b>📄 Terms of Service</b>"},
    "tos.empty":     {"ru": "ToS не задан.",                          "en": "Terms are not set."},
    "support.title": {"ru": "<b>🆘 Тех. поддержка</b>",               "en": "<b>🆘 Support</b>"},
    "support.empty": {"ru": "Контакт поддержки не задан.",            "en": "Support contact is not set."},

    # ── settings ───────────────────────────────────────────────────────────
    "settings.title": {
        "ru": "<b>⚙️ Настройки</b>\n\nТекущий язык: <b>{lang}</b>",
        "en": "<b>⚙️ Settings</b>\n\nCurrent language: <b>{lang}</b>",
    },
    "settings.btn.lang": {"ru": "🌐 Сменить язык", "en": "🌐 Change language"},

    # ── catalog ────────────────────────────────────────────────────────────
    "catalog.root":      {"ru": "🛒 Товары",                     "en": "🛒 Products"},
    "catalog.empty":     {"ru": "Здесь пока ничего нет.",         "en": "Nothing here yet."},
    "catalog.pick":      {"ru": "Выбери раздел или товар:",       "en": "Pick a section or item:"},
    "catalog.btn.back":  {"ru": "« Назад",                        "en": "« Back"},
    "catalog.btn.home":  {"ru": "🏠 В меню",                      "en": "🏠 Menu"},
    "catalog.notfound":  {"ru": "Категория не найдена.",          "en": "Category not found."},

    # ── product card ───────────────────────────────────────────────────────
    "product.no_desc":   {"ru": "<i>Без описания</i>",            "en": "<i>No description</i>"},
    "product.price":     {"ru": "Цена: <b>{price}</b> ⭐",        "en": "Price: <b>{price}</b> ⭐"},
    "product.btn.buy":   {"ru": "💳 Купить за {price} ⭐",        "en": "💳 Buy for {price} ⭐"},
    "product.unavail":   {"ru": "Товар недоступен.",              "en": "Item unavailable."},

    # ── payment ────────────────────────────────────────────────────────────
    "pay.ok": {
        "ru": (
            "✅ Оплата прошла успешно!\n\n"
            "Куплено: <b>{name}</b>\n"
            "Списано: <b>{amount}</b> ⭐\n\n"
            "Скоро с вами свяжутся для выдачи. Спасибо за покупку!"
        ),
        "en": (
            "✅ Payment successful!\n\n"
            "Item: <b>{name}</b>\n"
            "Charged: <b>{amount}</b> ⭐\n\n"
            "We'll contact you shortly for delivery. Thanks for your purchase!"
        ),
    },

    # ── subscription gate ──────────────────────────────────────────────────
    "sub.required": {
        "ru": "Чтобы пользоваться ботом, подпишитесь на наш канал.",
        "en": "Please subscribe to our channel to use the bot.",
    },
    "sub.btn.channel": {"ru": "📢 Перейти в канал", "en": "📢 Open channel"},
    "sub.btn.check":   {"ru": "✅ Я подписался",    "en": "✅ I subscribed"},
    "sub.not_yet":     {"ru": "Сначала подпишитесь на канал.", "en": "Please subscribe first."},

    # ── ban ────────────────────────────────────────────────────────────────
    "ban.notice": {"ru": "⛔ Вы заблокированы.", "en": "⛔ You are banned."},
}


def t(lang: str | None, key: str, /, **kwargs) -> str:
    """Translate `key` for given language; fall back to DEFAULT_LANG, then key itself.

    `lang` and `key` are positional-only so they don't clash with template
    placeholders of the same name (e.g. `{lang}` in 'settings.title').
    """
    lang = lang or DEFAULT_LANG
    entry = TRANSLATIONS.get(key, {})
    template = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    return template.format(**kwargs) if kwargs else template
