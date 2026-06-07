from telegram import Update
from telegram.ext import ContextTypes


async def resentment_inventory(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "💢 Инвентаризация обид\n\n"
        "Опиши свою обиду подробно."
    )
