import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.decorators import is_registered
from utils.error_handler import log_error


def command():
    @is_registered
    async def record_activities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            context.user_data.clear()
            user = update.effective_user
            keyboard = [[InlineKeyboardButton("🥤 Water", callback_data=json.dumps({'id': 'water'})),
                         InlineKeyboardButton("😴 Sleep", callback_data=json.dumps({'id': 'sleep'})),
                         InlineKeyboardButton("🏋🏻 Exercise", callback_data=json.dumps({'id': 'exercise'}))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_html(
                text=f"Hola {user.mention_html()}! 👋🏻\n\nWhich activity you want to record?",
                reply_markup=reply_markup
            )
        except Exception as e:
            log_error(e, 'Error in record_activities function.')
            await update.message.reply_html(
                text="An error occurred while processing your request, please try again later. 😢",
            )

    return record_activities
