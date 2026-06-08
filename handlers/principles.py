from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.principles_service import load_principles


PAGE_SIZE = 20


def build_principles_page(page):
    principles = load_principles()
    total = len(principles)

    if total == 0:
        return "Справочник принципов пока пуст.", None

    max_page = max((total - 1) // PAGE_SIZE, 0)
    page = max(0, min(page, max_page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    lines = [
        "📚 Духовные принципы",
        f"Страница {page + 1} из {max_page + 1}",
        "",
    ]

    for item in principles[start:end]:
        lines.append(
            f"{item.get('id')}. {item.get('name')}"
        )

    buttons = []

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"principles:page:{page - 1}"))
    if page < max_page:
        nav.append(InlineKeyboardButton("➡️ Далее", callback_data=f"principles:page:{page + 1}"))

    if nav:
        buttons.append(nav)

    return "\n".join(lines), InlineKeyboardMarkup(buttons) if buttons else None


async def show_principles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = build_principles_page(0)
    await update.message.reply_text(text, reply_markup=keyboard)


async def handle_principles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    page = int(parts[2])

    text, keyboard = build_principles_page(page)
    await query.edit_message_text(text, reply_markup=keyboard)
