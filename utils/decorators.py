import os
from functools import wraps

import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes

import settings


def is_registered(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_code = update.effective_user.id
        db = await aiosqlite.connect(os.path.join(settings.DATA_DIRECTORY_PATH, 'database', 'data.db'))
        cursor = await db.execute('SELECT * FROM users WHERE user_id = (?)', (user_code,))
        is_present = await cursor.fetchone()
        await cursor.close()
        await db.close()
        if is_present:
            return await func(update, context)
        else:
            await update.message.reply_html(text="You are not registered, please send\n/register to start your "
                                                 "registration process!")

    return wrapper
