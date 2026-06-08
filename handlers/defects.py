from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.defects_service import load_defects


PAGE_SIZE = 20


def build_defects_page(page):
    defects = load_defects()
    total = len(defects)

    if total == 0:
        return "Справочник дефектов пока пуст.", None

    max_page = max((total - 1) // PAGE_SIZE, 0)
    page = max(0, min(page, max_page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    lines = [
        "🧩 Дефекты характера",
        f"Страница {page + 1} из {max_page + 1}",
        "",
    ]

    for item in defects[start:end]:
        lines.append(
            f"{item.get('id')}. {item.get('name')} — {item.get('category')}"
        )

    buttons = []

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"defects:page:{page - 1}"))
    if page < max_page:
        nav.append(InlineKeyboardButton("➡️ Далее", callback_data=f"defects:page:{page + 1}"))

    if nav:
        buttons.append(nav)

    return "\n".join(lines), InlineKeyboardMarkup(buttons) if buttons else None


async def show_defects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = build_defects_page(0)
    await update.message.reply_text(text, reply_markup=keyboard)


async def handle_defects_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    page = int(parts[2])

    text, keyboard = build_defects_page(page)
    await query.edit_message_text(text, reply_markup=keyboard)
