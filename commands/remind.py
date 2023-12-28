import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.decorators import is_registered


def command():
    @is_registered
    async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data.clear()
        keyboard = [[InlineKeyboardButton("🔂 Once", callback_data=json.dumps({'id': 'once'})),
                     InlineKeyboardButton("🔁 Repeat", callback_data=json.dumps({'id': 'repeat'})), ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_html(
            text=f"Let's setup a custom reminder for you! 🛎️\n\nSelect the type of your reminder:",
            reply_markup=reply_markup
        )

    return remind
