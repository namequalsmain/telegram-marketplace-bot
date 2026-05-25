"""Typed CallbackData factories.

Why bother:
  - Single source of truth for callback formats (rename a field, IDE catches it).
  - Filter by field value: `@router.callback_query(Menu.filter(F.action == 'profile'))`
  - Handler receives a parsed object instead of `call.data.split(':')`.
"""

from aiogram.filters.callback_data import CallbackData


# ─── User side ──────────────────────────────────────────────────────────────
class Menu(CallbackData, prefix="m"):
    action: str  # home | profile | tos | support | settings


class Catalog(CallbackData, prefix="c"):
    """Open a catalog node. id=0 means the virtual root."""
    id: int


class Product(CallbackData, prefix="p"):
    action: str  # view | buy
    id: int


class Lang(CallbackData, prefix="l"):
    target: str  # set (initial pick) | change (from settings)
    code: str    # 'ru' | 'en' | ...


class SettingsAction(CallbackData, prefix="s"):
    action: str  # open_lang


# ─── Admin side ─────────────────────────────────────────────────────────────
class Admin(CallbackData, prefix="a"):
    action: str  # home | broadcast | stats | users | settings


class AdminCat(CallbackData, prefix="ac"):
    """Open admin view of a category. id=0 = root."""
    id: int


class AdminCatAction(CallbackData, prefix="aca"):
    action: str  # add | rename | delete
    id: int      # parent for add, self for rename/delete


class AdminProd(CallbackData, prefix="ap"):
    action: str  # view | toggle | delete | add
    id: int      # product id for view/toggle/delete, category id for add


class AdminBroadcast(CallbackData, prefix="abc"):
    action: str  # send | cancel


class AdminUserAction(CallbackData, prefix="auser"):
    action: str  # ban | unban | promote | demote


class AdminSetting(CallbackData, prefix="aset"):
    action: str  # toggle_sub | edit
    key: str = ""
