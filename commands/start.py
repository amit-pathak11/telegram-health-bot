from telegram import Update
from telegram.ext import ContextTypes


def command():
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hi {user.mention_html()}, DemoBot welcomes you!\nThis bot will fetch you the random quotes "
                 f"list.\nTo get started send <b>/list</b>.",
            parse_mode="HTML",
        )

    return start
