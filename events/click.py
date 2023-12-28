import json

from telegram import ReplyKeyboardMarkup

from utils.error_handler import log_error
from utils.helper import check_cooldown


async def click_callback(update, context):
    try:
        user = update.effective_user
        user_code = user.id
        query = update.callback_query
        query_data = json.loads(query.data)
        record_list = ['water', 'sleep', 'exercise']
        btn_id = query_data['id']
        await query.answer()
        if btn_id in record_list:
            cooldown = await check_cooldown(user_code, btn_id)
            context.user_data.clear()
            if cooldown[0]:
                # Insert the record
                if btn_id == 'water':
                    msg = '🚰 So how much water did you drink today? 🚰'
                    keyboard = [[str(water) + 'L'] for water in range(1, 11)]
                elif btn_id == 'sleep':
                    msg = '💤 How much did you sleep today? 💤'
                    keyboard = [[str(sleep) + ' Hrs'] for sleep in range(1, 25)]
                else:
                    msg = '🚴🏻 Have you done enough exercise today? 🤸'
                    keyboard = [[str(exercise) + ' Minutes'] for exercise in range(30, 181, 30)]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

                # Delete the existing message
                await query.delete_message()
                # Send new message with ReplyKeyboardMarkup
                await query.message.reply_html(text=msg, reply_markup=reply_markup)
                context.user_data['record_step'] = btn_id
            else:
                # Show cooldown time
                await query.edit_message_text(f'Not So Fast {user.mention_html()}! ⏳\n\nYou have to wait for - <pre>\n'
                                              f'{cooldown[1]}\n</pre>', parse_mode='HTML')
        else:
            await query.delete_message()
            context.user_data['reminder_step'] = btn_id
            await query.message.reply_html(f"📌 What's the purpose behind this reminder?")
    except Exception as e:
        log_error(e, 'Error in click_callback function.')
        await update.callback_query.edit_message_text(
            text="An error occurred while processing your request, please try again later. 😢",
        )
