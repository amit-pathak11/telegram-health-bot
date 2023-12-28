from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from utils.error_handler import log_error
from utils.helper import get_user


def command_register():
    async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            context.user_data.clear()
            user = update.effective_user
            if not await get_user(user.id):
                registration_step = context.user_data.get('registration_step')
                if not registration_step:
                    # Start the registration process
                    await update.message.reply_html(
                        text=f"<b>Hey there {user.mention_html()}!</b>"
                             f"\n\nAt any point you want to cancel the registration process, just send /cancel"
                             f"\n\nLet's start your registration process. 📝"
                             f"\nPlease enter your <b>First Name</b>:"
                    )
                    # Set the next step to 'name'
                    context.user_data['registration_step'] = 'name'
                else:
                    await update.message.reply_html(
                        text=f"Your registration process is already in progress!"
                    )
                    return
            else:
                await update.message.reply_html(
                    text="It seems like you are already registered! 🤔",
                )
        except Exception as e:
            log_error(e, 'Failed to register user')
            await update.message.reply_html(
                text="An error occurred while processing your request, please try again later. 😢",
            )

    return register


def command_cancel():
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            registration_step = context.user_data.get('registration_step')
            if registration_step:
                # Start the registration process
                await update.message.reply_html(
                    text=f"Registration process cancelled! ❌",
                    reply_markup=ReplyKeyboardRemove(),
                )
                # Clear registration data
                context.user_data.clear()
            else:
                await update.message.reply_html(
                    text=f"You don't have any active registration process!"
                )
                return
        except Exception as e:
            log_error(e, 'Failed to cancel registration process')
            await update.message.reply_html(
                text="An error occurred while processing your request, please try again later. 😢",
            )

    return cancel
