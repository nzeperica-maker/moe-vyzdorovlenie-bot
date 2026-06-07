from telegram import Update
from telegram.ext import ContextTypes


async def fear_inventory(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "😨 Инвентаризация страхов\n\n"
        "Опиши свой страх подробно."
    )
