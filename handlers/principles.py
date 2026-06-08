from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import random

from services.database import supabase
from services.principles_service import load_principles, get_principle_by_id
from services.principles_seed import seed_principles


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


def principles_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Карточки принципов", callback_data="principles:cards:0")],
        [InlineKeyboardButton("🌅 Принцип дня", callback_data="principles:day")],
        [
            InlineKeyboardButton("😨 Для страхов", callback_data="principles:category:fears:0"),
            InlineKeyboardButton("💢 Для обид", callback_data="principles:category:resentments:0"),
        ],
        [InlineKeyboardButton("🧩 Для дефектов", callback_data="principles:category:defects:0")],
        [InlineKeyboardButton("⭐ Избранное", callback_data="principles:favorites")],
        [InlineKeyboardButton("📚 Полный справочник", callback_data="principles:list:0")],
    ])


def back_to_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ В меню принципов", callback_data="principles:menu")]
    ])


async def show_principles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Духовные принципы</b>\n\n"
        "Выбери формат изучения:",
        reply_markup=principles_menu_keyboard(),
        parse_mode="HTML"
    )


def build_full_list_page(page):
    principles = load_principles()

    if not principles:
        return (
            "📚 <b>Справочник принципов пуст</b>\n\n"
            "Напиши команду /seed_principles",
            None
        )

    max_page = max((len(principles) - 1) // PAGE_SIZE, 0)
    page = max(0, min(page, max_page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = (
        "📚 <b>Полный справочник</b>\n\n"
        f"Страница {page + 1} из {max_page + 1}\n"
        f"Всего принципов: {len(principles)}\n\n"
    )

    for item in principles[start:end]:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"{short_text(item.get('description'), 700)}\n\n"
        )

    buttons = []

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"principles:list:{page - 1}"
            )
        )

    if page < max_page:
        nav.append(
            InlineKeyboardButton(
                "➡️ Далее",
                callback_data=f"principles:list:{page + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("⬅️ В меню принципов", callback_data="principles:menu")
    ])

    return text, InlineKeyboardMarkup(buttons)


def check_favorite(user_id, principle_id):
    result = (
        supabase.table("favorite_principles")
        .select("id")
        .eq("telegram_id", user_id)
        .eq("principle_id", principle_id)
        .execute()
    )

    return bool(result.data)


def toggle_favorite(user_id, principle_id):
    if check_favorite(user_id, principle_id):
        (
            supabase.table("favorite_principles")
            .delete()
            .eq("telegram_id", user_id)
            .eq("principle_id", principle_id)
            .execute()
        )
        return False

    supabase.table("favorite_principles").insert({
        "telegram_id": user_id,
        "principle_id": principle_id
    }).execute()

    return True


def build_card(index, user_id):
    principles = load_principles()

    if not principles:
        return (
            "📚 <b>Справочник принципов пуст</b>\n\n"
            "Напиши команду /seed_principles",
            None
        )

    index = max(0, min(index, len(principles) - 1))
    item = principles[index]

    is_favorite = check_favorite(user_id, item.get("id"))
    star_text = "⭐ Убрать из избранного" if is_favorite else "⭐ В избранное"

    text = (
        "📖 <b>Карточка принципа</b>\n\n"
        f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n\n"
        f"{short_text(item.get('description'), 2500)}\n\n"
        f"Карточка {index + 1} из {len(principles)}"
    )

    buttons = []

    nav = []
    if index > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Предыдущий",
                callback_data=f"principles:cards:{index - 1}"
            )
        )

    if index < len(principles) - 1:
        nav.append(
            InlineKeyboardButton(
                "➡️ Следующий",
                callback_data=f"principles:cards:{index + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton(
            star_text,
            callback_data=f"principles:favorite:{item.get('id')}:{index}"
        )
    ])

    buttons.append([
        InlineKeyboardButton("⬅️ В меню принципов", callback_data="principles:menu")
    ])

    return text, InlineKeyboardMarkup(buttons)


def get_principle_day(user_id):
    today = datetime.now().strftime("%Y-%m-%d")

    existing = (
        supabase.table("daily_principles")
        .select("*")
        .eq("telegram_id", user_id)
        .eq("day", today)
        .limit(1)
        .execute()
    )

    if existing.data:
        return get_principle_by_id(existing.data[0]["principle_id"])

    principles = load_principles()

    if not principles:
        return None

    item = random.choice(principles)

    supabase.table("daily_principles").insert({
        "telegram_id": user_id,
        "principle_id": item["id"],
        "day": today
    }).execute()

    return item


def build_day_principle(user_id):
    item = get_principle_day(user_id)

    if not item:
        return (
            "🌅 <b>Принцип дня</b>\n\n"
            "Справочник пуст. Напиши /seed_principles.",
            back_to_menu_keyboard()
        )

    text = (
        "🌅 <b>Принцип дня</b>\n\n"
        f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n\n"
        f"{short_text(item.get('description'), 2500)}\n\n"
        "Попробуй сегодня заметить, где этот принцип можно применить в действиях."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⭐ В избранное / убрать",
                callback_data=f"principles:favorite:{item.get('id')}:day"
            )
        ],
        [InlineKeyboardButton("⬅️ В меню принципов", callback_data="principles:menu")],
    ])

    return text, keyboard


def category_keywords(category):
    if category == "fears":
        return [
            "страх",
            "бессилие",
            "смирение",
            "бог",
            "вс",
            "только сегодня",
            "помощь",
            "доверие",
        ]

    if category == "resentments":
        return [
            "обид",
            "прощ",
            "терпим",
            "любов",
            "ожидан",
            "новый взгляд",
            "принятие",
        ]

    if category == "defects":
        return [
            "эго",
            "корыст",
            "самообман",
            "своевол",
            "дефект",
            "ошиб",
            "чест",
            "ответственность",
        ]

    return []


def category_title(category):
    if category == "fears":
        return "😨 Принципы для страхов"

    if category == "resentments":
        return "💢 Принципы для обид"

    if category == "defects":
        return "🧩 Принципы для дефектов"

    return "📚 Подборка принципов"


def build_category_page(category, page):
    principles = load_principles()
    keywords = category_keywords(category)

    filtered = []

    for item in principles:
        haystack = f"{item.get('name', '')} {item.get('description', '')}".lower()

        if any(word in haystack for word in keywords):
            filtered.append(item)

    if not filtered:
        return (
            f"{category_title(category)}\n\n"
            "Пока нет подходящих принципов.",
            back_to_menu_keyboard()
        )

    max_page = max((len(filtered) - 1) // PAGE_SIZE, 0)
    page = max(0, min(page, max_page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = (
        f"<b>{category_title(category)}</b>\n\n"
        f"Страница {page + 1} из {max_page + 1}\n\n"
    )

    for item in filtered[start:end]:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"{short_text(item.get('description'), 650)}\n\n"
        )

    buttons = []

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"principles:category:{category}:{page - 1}"
            )
        )

    if page < max_page:
        nav.append(
            InlineKeyboardButton(
                "➡️ Далее",
                callback_data=f"principles:category:{category}:{page + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("⬅️ В меню принципов", callback_data="principles:menu")
    ])

    return text, InlineKeyboardMarkup(buttons)


def build_favorites(user_id):
    result = (
        supabase.table("favorite_principles")
        .select("principle_id")
        .eq("telegram_id", user_id)
        .execute()
    )

    if not result.data:
        return (
            "⭐ <b>Избранные принципы</b>\n\n"
            "Ты пока ничего не добавила в избранное.",
            back_to_menu_keyboard()
        )

    ids = [item["principle_id"] for item in result.data]

    principles = (
        supabase.table("principles")
        .select("*")
        .in_("id", ids)
        .order("source_number")
        .execute()
        .data
        or []
    )

    text = "⭐ <b>Избранные принципы</b>\n\n"

    for item in principles:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"{short_text(item.get('description'), 500)}\n\n"
        )

    return text, back_to_menu_keyboard()


async def handle_principles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    parts = query.data.split(":")
    action = parts[1]

    if action == "menu":
        await query.edit_message_text(
            "📚 <b>Духовные принципы</b>\n\n"
            "Выбери формат изучения:",
            reply_markup=principles_menu_keyboard(),
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
        text, keyboard = build_day_principle(user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    if action == "category":
        category = parts[2]
        page = int(parts[3]) if len(parts) > 3 else 0
        text, keyboard = build_category_page(category, page)

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
        principle_id = int(parts[2])
        back = parts[3] if len(parts) > 3 else "0"

        toggle_favorite(user_id, principle_id)

        if back == "day":
            text, keyboard = build_day_principle(user_id)
        else:
            text, keyboard = build_card(int(back), user_id)

        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return


async def seed_principles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = seed_principles()

    await update.message.reply_text(
        "✅ Справочник духовных принципов загружен в облако.\n\n"
        f"Добавлено/обновлено: {count}"
    )
