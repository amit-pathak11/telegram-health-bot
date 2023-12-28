import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

import settings
from commands import register, record, report, remind, card
from events import on_message, click

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        text=f"Welcome to <b>Health Tracker Bot</b>! 🤖✨"
             f"\n\nI'm here to help you to record your daily activities, provide weekly "
             f"health reports, offer custom reminders, and display your personalized health card!"
             f"\n\nLet's embark on a journey to a healthier you together! 🌟"
             f"\n\n💠 Send <b>/help</b> to know more about me and get started.",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        text=f"📟 <b>Full List Of Commands</b> 📟\n\n"
             "\n/start - Get the intro message of the bot."
             "\n/help - Shows the list of available commands."
             "\n/register - Start your registration process."
             "\n/record - Record your daily activities."
             "\n/remind - Setup a custom reminder."
             "\n/report - Get your health report for this week."
             "\n/card - Get your personalized health card."
    )


def main() -> None:
    application = Application.builder().token(settings.TOKEN).build()

    try:
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_cmd))

        # Module commands
        application.add_handler(CommandHandler("record", record.command()))
        application.add_handler(CommandHandler("remind", remind.command()))
        application.add_handler(CommandHandler("report", report.command()))
        application.add_handler(CommandHandler("card", card.command()))

        application.add_handler(CommandHandler("register", register.command_register()))
        application.add_handler(CommandHandler("cancel", register.command_cancel()))

        # Event handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message.handle_registration))
        application.add_handler(CallbackQueryHandler(click.click_callback))

    except Exception as e:
        logger.error(f'error setting up the bot {str(e)}')

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    main()
