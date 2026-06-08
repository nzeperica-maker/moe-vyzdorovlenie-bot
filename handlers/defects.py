from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import random

from services.database import supabase
from services.defects_service import load_defects, get_defect_by_id
from services.defects_seed import seed_defects


PAGE_SIZE = 5


def safe_html(text):
    if text is None:
        return "—"

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def short_text(text, limit=1200):
    text = safe_html(text)

    if len(text) <= limit:
        return text

    return text[:limit] + "..."


def list_to_text(items):
    if not items:
        return "—"

    if isinstance(items, str):
        return items

    return "\n".join(f"• {item}" for item in items)


def defects_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Карточки дефектов", callback_data="defects:cards:0")],
        [InlineKeyboardButton("🔥 Дефект дня", callback_data="defects:day")],
        [InlineKeyboardButton("🛠 Инструменты работы", callback_data="defects:tools")],
        [InlineKeyboardButton("⭐ Избранное", callback_data="defects:favorites")],
        [InlineKeyboardButton("📚 Полный справочник", callback_data="defects:list:0")],
    ])


def back_to_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ В меню дефектов", callback_data="defects:menu")]
    ])


async def show_defects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧩 <b>Дефекты характера</b>\n\n"
        "Выбери формат изучения:",
        reply_markup=defects_menu_keyboard(),
        parse_mode="HTML"
    )


def build_full_list_page(page):
    defects = load_defects()

    if not defects:
        return (
            "🧩 <b>Справочник дефектов пуст</b>\n\n"
            "Напиши команду /seed_defects",
            None
        )

    max_page = max((len(defects) - 1) // PAGE_SIZE, 0)
    page = max(0, min(page, max_page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = (
        "📚 <b>Полный справочник дефектов</b>\n\n"
        f"Страница {page + 1} из {max_page + 1}\n"
        f"Всего дефектов: {len(defects)}\n\n"
    )

    for item in defects[start:end]:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"Категория: {safe_html(item.get('category'))}\n"
            f"{short_text(item.get('description'), 700)}\n\n"
        )

    buttons = []

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"defects:list:{page - 1}"
            )
        )

    if page < max_page:
        nav.append(
            InlineKeyboardButton(
                "➡️ Далее",
                callback_data=f"defects:list:{page + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("⬅️ В меню дефектов", callback_data="defects:menu")
    ])

    return text, InlineKeyboardMarkup(buttons)


def check_favorite(user_id, defect_id):
    result = (
        supabase.table("favorite_defects")
        .select("id")
        .eq("telegram_id", user_id)
        .eq("defect_id", defect_id)
        .execute()
    )

    return bool(result.data)


def toggle_favorite(user_id, defect_id):
    if check_favorite(user_id, defect_id):
        (
            supabase.table("favorite_defects")
            .delete()
            .eq("telegram_id", user_id)
            .eq("defect_id", defect_id)
            .execute()
        )
        return False

    supabase.table("favorite_defects").insert({
        "telegram_id": user_id,
        "defect_id": defect_id
    }).execute()

    return True


def build_card(index, user_id):
    defects = load_defects()

    if not defects:
        return (
            "🧩 <b>Справочник дефектов пуст</b>\n\n"
            "Напиши команду /seed_defects",
            None
        )

    index = max(0, min(index, len(defects) - 1))
    item = defects[index]

    is_favorite = check_favorite(user_id, item.get("id"))
    star_text = "⭐ Убрать из избранного" if is_favorite else "⭐ В избранное"

    text = (
        "📖 <b>Карточка дефекта</b>\n\n"
        f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n\n"
        f"<b>Категория:</b>\n{safe_html(item.get('category'))}\n\n"
        f"<b>Описание:</b>\n{short_text(item.get('description'), 1800)}\n\n"
        f"<b>Принципы для работы:</b>\n"
        f"{safe_html(list_to_text(item.get('related_principles')))}\n\n"
        f"Карточка {index + 1} из {len(defects)}"
    )

    buttons = []

    nav = []

    if index > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Предыдущий",
                callback_data=f"defects:cards:{index - 1}"
            )
        )

    if index < len(defects) - 1:
        nav.append(
            InlineKeyboardButton(
                "➡️ Следующий",
                callback_data=f"defects:cards:{index + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton(
            star_text,
            callback_data=f"defects:favorite:{item.get('id')}:{index}"
        )
    ])

    buttons.append([
        InlineKeyboardButton("⬅️ В меню дефектов", callback_data="defects:menu")
    ])

    return text, InlineKeyboardMarkup(buttons)


def get_defect_day(user_id):
    today = datetime.now().strftime("%Y-%m-%d")

    existing = (
        supabase.table("daily_defects")
        .select("*")
        .eq("telegram_id", user_id)
        .eq("day", today)
        .limit(1)
        .execute()
    )

    if existing.data:
        return get_defect_by_id(existing.data[0]["defect_id"])

    defects = load_defects()

    if not defects:
        return None

    item = random.choice(defects)

    supabase.table("daily_defects").insert({
        "telegram_id": user_id,
        "defect_id": item["id"],
        "day": today
    }).execute()

    return item


def build_day_defect(user_id):
    item = get_defect_day(user_id)

    if not item:
        return (
            "🔥 <b>Дефект дня</b>\n\n"
            "Справочник пуст. Напиши /seed_defects.",
            back_to_menu_keyboard()
        )

    text = (
        "🔥 <b>Дефект дня</b>\n\n"
        f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n\n"
        f"<b>Категория:</b>\n{safe_html(item.get('category'))}\n\n"
        f"<b>Описание:</b>\n{short_text(item.get('description'), 1800)}\n\n"
        f"<b>Принципы для работы:</b>\n"
        f"{safe_html(list_to_text(item.get('related_principles')))}\n\n"
        "Сегодня попробуй замечать, где этот дефект проявляется в мыслях, чувствах и действиях."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⭐ В избранное / убрать",
                callback_data=f"defects:favorite:{item.get('id')}:day"
            )
        ],
        [InlineKeyboardButton("⬅️ В меню дефектов", callback_data="defects:menu")],
    ])

    return text, keyboard


def build_tools():
    text = (
        "🛠 <b>Инструменты работы с дефектами</b>\n\n"
        "<b>1. Пауза</b>\n"
        "Не отвечать сразу. Остановиться, подышать, не усиливать реакцию.\n\n"
        "<b>2. Инвентаризация</b>\n"
        "Записать: что произошло, что я почувствовал(а), чего испугался(лась), где моя ответственность.\n\n"
        "<b>3. Молитва / обращение к ВС</b>\n"
        "Попросить освободить от дефекта и показать правильное действие.\n\n"
        "<b>4. Честность</b>\n"
        "Назвать истинный мотив: чего я хотел(а), что пытался(лась) получить или контролировать.\n\n"
        "<b>5. Обсуждение со спонсором</b>\n"
        "Не оставаться одному/одной в голове. Проговорить ситуацию.\n\n"
        "<b>6. Принцип вместо дефекта</b>\n"
        "Выбрать духовный принцип и сделать конкретное действие по нему.\n\n"
        "<b>7. Возмещение ущерба</b>\n"
        "Если был причинён вред — признать его и исправить безопасным способом.\n\n"
        "<b>8. Служение</b>\n"
        "Сделать полезное действие без ожидания выгоды."
    )

    return text, back_to_menu_keyboard()


def build_favorites(user_id):
    result = (
        supabase.table("favorite_defects")
        .select("defect_id")
        .eq("telegram_id", user_id)
        .execute()
    )

    if not result.data:
        return (
            "⭐ <b>Избранные дефекты</b>\n\n"
            "Ты пока ничего не добавила в избранное.",
            back_to_menu_keyboard()
        )

    ids = [item["defect_id"] for item in result.data]

    defects = (
        supabase.table("defects")
        .select("*")
        .in_("id", ids)
        .order("source_number")
        .execute()
        .data
        or []
    )

    text = "⭐ <b>Избранные дефекты</b>\n\n"

    for item in defects:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"Категория: {safe_html(item.get('category'))}\n"
            f"{short_text(item.get('description'), 500)}\n\n"
        )

    return text, back_to_menu_keyboard()


async def handle_defects_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    parts = query.data.split(":")
    action = parts[1]

    if action == "menu":
        await query.edit_message_text(
            "🧩 <b>Дефекты характера</b>\n\n"
            "Выбери формат изучения:",
            reply_markup=defects_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    if action == "list":
        page = int(parts[2])
        text, keyboard = build_full_list_page(page)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "cards":
        index = int(parts[2])
        text, keyboard = build_card(index, user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "day":
        text, keyboard = build_day_defect(user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "tools":
        text, keyboard = build_tools()

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "favorites":
        text, keyboard = build_favorites(user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "favorite":
        defect_id = int(parts[2])
        back = parts[3] if len(parts) > 3 else "0"

        toggle_favorite(user_id, defect_id)

        if back == "day":
            text, keyboard = build_day_defect(user_id)
        else:
            text, keyboard = build_card(int(back), user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return


async def seed_defects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = seed_defects()

    await update.message.reply_text(
        "✅ Справочник дефектов загружен в облако.\n\n"
        f"Добавлено/обновлено: {count}"
    )
