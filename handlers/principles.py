from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.principles_service import load_principles
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


def build_principles_page(page):
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
        "📚 <b>Духовные принципы</b>\n\n"
        f"Страница {page + 1} из {max_page + 1}\n"
        f"Всего принципов: {len(principles)}\n\n"
    )

    for item in principles[start:end]:
        text += (
            f"<b>{item.get('source_number')}. {safe_html(item.get('name'))}</b>\n"
            f"{safe_html(item.get('description'))}\n\n"
        )

    buttons = []

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"principles:page:{page - 1}"
            )
        )

    if page < max_page:
        nav.append(
            InlineKeyboardButton(
                "➡️ Далее",
                callback_data=f"principles:page:{page + 1}"
            )
        )

    if nav:
        buttons.append(nav)

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    return text, keyboard


async def show_principles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = build_principles_page(0)

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def handle_principles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[2])
    text, keyboard = build_principles_page(page)

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def seed_principles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = seed_principles()

    await update.message.reply_text(
        "✅ Справочник духовных принципов загружен в облако.\n\n"
        f"Добавлено/обновлено: {count}"
    )
