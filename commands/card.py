import os

from telegram import Update
from telegram.ext import ContextTypes

import settings
from utils.decorators import is_registered
from utils.error_handler import log_error
from utils.helper import get_health_card


def command():
    @is_registered
    async def card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            user = update.effective_user
            get_pfp = await user.get_profile_photos(limit=1)
            if get_pfp.photos:
                # Download the photo
                pfp = os.path.join(settings.DATA_DIRECTORY_PATH, 'images', 'user_pictures', f'{user.id}.jpg')
                photo = get_pfp.photos[-1][-1]
                file = await context.bot.get_file(photo.file_id)
                await file.download_to_drive(pfp)
            else:
                pfp = os.path.join(settings.DATA_DIRECTORY_PATH, 'images', 'default.jpg')
            get_card = await get_health_card(user.id, pfp)
            await update.message.reply_photo(
                photo=get_card,
                caption=f"<b>{user.mention_html()}'s Health Card</b>",
                parse_mode="HTML",
                filename='Health Card'
            )
        except Exception as e:
            log_error(e, 'Error in card function.')
            await update.message.reply_html(
                text="An error occurred while processing your request, please try again later. 😢",
            )

    return card
