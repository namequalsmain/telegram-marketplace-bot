"""Admin CRUD for categories and products."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.keyboards import (
    back_to_admin,
    catalog_node,
    product_card,
)
from bot.callbacks import AdminCat, AdminCatAction, AdminProd
from bot.filters import IsAdmin
from bot.utils import send_or_edit
from database.repo import categories as categories_repo
from database.repo import products as products_repo

router = Router(name="admin_catalog")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class CategoryForm(StatesGroup):
    add_name = State()
    rename = State()


class ProductForm(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()


# ─── Show a node ────────────────────────────────────────────────────────────
async def _show_node(target, session: AsyncSession, category_id: int) -> None:
    """Render category node by id (0 = root)."""
    category = None
    if category_id != 0:
        category = await categories_repo.get(session, category_id)
        if category is None:
            if isinstance(target, CallbackQuery):
                await target.answer("Категория не найдена.", show_alert=True)
            return

    children = await categories_repo.children_of(
        session, category.id if category else None
    )
    products = await products_repo.in_category(session, category.id) if category else []

    crumbs = (
        ["📁 Корень"]
        + [c.name for c in await categories_repo.breadcrumbs(session, category.id)]
    ) if category else ["📁 Корень"]

    body = "Пусто." if not children and not products else "Содержимое:"
    text = f"<b>{' › '.join(crumbs)}</b>\n\n{body}"
    await send_or_edit(target, text, catalog_node(category, children, products))


@router.callback_query(AdminCat.filter())
async def cb_open(
    call: CallbackQuery, callback_data: AdminCat, session: AsyncSession, state: FSMContext
) -> None:
    await state.clear()
    await _show_node(call, session, callback_data.id)


# ─── Category: add / rename / delete ─────────────────────────────────────────
@router.callback_query(AdminCatAction.filter(F.action == "add"))
async def cb_cat_add(call: CallbackQuery, callback_data: AdminCatAction, state: FSMContext) -> None:
    await state.set_state(CategoryForm.add_name)
    await state.update_data(parent_id=callback_data.id or None)
    await call.message.answer("Введи название новой категории (/cancel — отмена):")
    await call.answer()


@router.message(CategoryForm.add_name)
async def form_cat_add(message: Message, state: FSMContext, session: AsyncSession) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Пустое название не подойдёт. Введи ещё раз:")
        return
    data = await state.get_data()
    await categories_repo.create(session, data.get("parent_id"), name[:128])
    await state.clear()
    await message.answer(f"✅ Категория «{name}» создана.", reply_markup=back_to_admin())


@router.callback_query(AdminCatAction.filter(F.action == "rename"))
async def cb_cat_rename(call: CallbackQuery, callback_data: AdminCatAction, state: FSMContext) -> None:
    await state.set_state(CategoryForm.rename)
    await state.update_data(cat_id=callback_data.id)
    await call.message.answer("Введи новое название (/cancel — отмена):")
    await call.answer()


@router.message(CategoryForm.rename)
async def form_cat_rename(message: Message, state: FSMContext, session: AsyncSession) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Пустое название не подойдёт. Введи ещё раз:")
        return
    data = await state.get_data()
    cat = await categories_repo.get(session, data["cat_id"])
    if cat:
        await categories_repo.rename(session, cat, name[:128])
    await state.clear()
    await message.answer("✅ Переименовано.", reply_markup=back_to_admin())


@router.callback_query(AdminCatAction.filter(F.action == "delete"))
async def cb_cat_delete(
    call: CallbackQuery, callback_data: AdminCatAction, session: AsyncSession
) -> None:
    cat = await categories_repo.get(session, callback_data.id)
    if cat is None:
        await call.answer("Не найдено.", show_alert=True)
        return
    parent = cat.parent_id if cat.parent_id else 0
    await categories_repo.delete(session, cat)
    await call.answer("Удалено.")
    await _show_node(call, session, parent)


# ─── Product: view / toggle / delete ────────────────────────────────────────
@router.callback_query(AdminProd.filter(F.action == "view"))
async def cb_prod_view(
    call: CallbackQuery, callback_data: AdminProd, session: AsyncSession
) -> None:
    p = await products_repo.get(session, callback_data.id)
    if p is None:
        await call.answer("Не найдено.", show_alert=True)
        return
    text = (
        f"<b>🛍 {p.name}</b>\n\n"
        f"{p.description or '<i>без описания</i>'}\n\n"
        f"Цена: <b>{p.price}</b> ⭐\n"
        f"Активен: {'да' if p.is_active else 'нет'}"
    )
    await send_or_edit(call, text, product_card(p))


@router.callback_query(AdminProd.filter(F.action == "toggle"))
async def cb_prod_toggle(
    call: CallbackQuery, callback_data: AdminProd, session: AsyncSession
) -> None:
    p = await products_repo.get(session, callback_data.id)
    if p is None:
        await call.answer("Не найдено.", show_alert=True)
        return
    await products_repo.toggle_active(session, p)
    await call.answer("Готово.")
    await cb_prod_view(call, callback_data, session)


@router.callback_query(AdminProd.filter(F.action == "delete"))
async def cb_prod_delete(
    call: CallbackQuery, callback_data: AdminProd, session: AsyncSession
) -> None:
    p = await products_repo.get(session, callback_data.id)
    if p is None:
        await call.answer("Не найдено.", show_alert=True)
        return
    category_id = p.category_id
    await products_repo.delete(session, p)
    await call.answer("Удалено.")
    await _show_node(call, session, category_id)


# ─── Product: add (FSM 4 steps: name → desc → price → photo) ────────────────
@router.callback_query(AdminProd.filter(F.action == "add"))
async def cb_prod_add(call: CallbackQuery, callback_data: AdminProd, state: FSMContext) -> None:
    if callback_data.id == 0:
        await call.answer("Нельзя добавить товар в корень — создай категорию.", show_alert=True)
        return
    await state.set_state(ProductForm.name)
    await state.update_data(category_id=callback_data.id)
    await call.message.answer("Шаг 1/4: введи название товара (/cancel — отмена):")
    await call.answer()


@router.message(ProductForm.name)
async def form_prod_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым. Введи ещё раз:")
        return
    await state.update_data(name=name[:128])
    await state.set_state(ProductForm.description)
    await message.answer("Шаг 2/4: введи описание ('-' чтобы пропустить):")


@router.message(ProductForm.description)
async def form_prod_desc(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    description = "" if raw == "-" else raw
    await state.update_data(description=description)
    await state.set_state(ProductForm.price)
    await message.answer("Шаг 3/4: цена в ⭐ (целое число ≥ 1):")


@router.message(ProductForm.price)
async def form_prod_price(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    try:
        price = int(raw)
        if price < 1:
            raise ValueError
    except ValueError:
        await message.answer("Цена должна быть целым числом ≥ 1. Повтори:")
        return
    await state.update_data(price=price)
    await state.set_state(ProductForm.photo)
    await message.answer("Шаг 4/4: пришли фото товара ('-' чтобы без фото):")


@router.message(ProductForm.photo)
async def form_prod_photo(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.photo:
        photo_id = message.photo[-1].file_id
    elif (message.text or "").strip() == "-":
        photo_id = None
    else:
        await message.answer("Пришли фото или '-':")
        return

    data = await state.get_data()
    product = await products_repo.create(
        session,
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price=data["price"],
        photo_file_id=photo_id,
    )
    await state.clear()
    await message.answer(
        f"✅ Товар «{product.name}» создан за {product.price} ⭐.",
        reply_markup=back_to_admin(),
    )
