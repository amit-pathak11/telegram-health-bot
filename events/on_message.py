import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from utils.error_handler import log_error
from utils.helper import (
    register_user,
    enter_record,
    check_name,
    check_gender,
    check_age,
    check_water,
    check_sleep,
    check_exercise, custom_reminder, get_user
)


async def error_message(update, context, message) -> None:
    step = ''
    if context.user_data.get('registration_step'):
        step = context.user_data.get('registration_step')
    elif context.user_data.get('record_step'):
        step = context.user_data.get('record_step')
    await update.message.reply_html(
        text=f"<b>Invalid {step.title()} Value!</b>\n\n<b>{message}</b>",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return


async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        user_code = user.id
        if context.user_data.get('registration_step'):
            registration_step = context.user_data.get('registration_step')
            if registration_step == 'name':
                name = update.message.text
                if check_name(name):
                    context.user_data['name'] = name

                    # Ask for the gender using an inline keyboard
                    keyboard = [['Male 👨🏻', 'Female 👩🏻']]
                    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                    await update.message.reply_html(
                        text="Nice name! 😃\nNow, please select your gender:",
                        reply_markup=reply_markup,
                        reply_to_message_id=update.message.message_id,  # Use ForceReply to hide the regular keyboard
                    )
                    # Set the next step to 'gender'
                    context.user_data['registration_step'] = 'gender'
                else:
                    await error_message(update, context,
                                        "The name must contain only letters and be at least 3 characters long.")
            elif registration_step == 'gender':
                gender = update.message.text
                if check_gender(gender):
                    context.user_data['gender'] = 'Male' if 'male' in gender.lower() else 'Female'

                    # Present a list of ages in an inline keyboard
                    age_options = [[str(age)] for age in range(18, 101)]  # Age range from 18 to 100
                    reply_markup = ReplyKeyboardMarkup(age_options, one_time_keyboard=True)
                    await update.message.reply_html(
                        text="Alright going good! 🙌🏻\nFinal step, please select your age:",
                        reply_markup=reply_markup,
                    )

                    # Set the next step to 'age'
                    context.user_data['registration_step'] = 'age'
                else:
                    await error_message(update, context, "You must choose either 'Male' or 'Female'.")
            elif registration_step == 'age':
                age = update.message.text
                if check_age(age):
                    name, gender, age = context.user_data['name'], context.user_data['gender'], int(age)
                    # End the registration process
                    await update.message.reply_html(
                        text="That's it, you have successfully registered your account! 🎉"
                             "\nSend /help to get started and "
                             "start recording your health data. 🎯",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    # Clear registration data
                    context.user_data.clear()
                    # Register the user in the database
                    await register_user(user_code, name, gender, age)
                    return
                else:
                    await error_message(update, context, "Age must be a number between 18 and 100.")
        elif context.user_data.get('record_step'):
            record_step = context.user_data.get('record_step')
            user_input = update.message.text
            msg, value = '', ''
            if record_step == 'water':
                value = check_water(user_input)
                if not value:
                    return await error_message(update, context,
                                               "⛔ Water intake must be a number greater than 0. ⛔\n\n↪️ Use this "
                                               "format: <code>6L</code> to record 6 litres of water intake.")
                msg = f'Successfully recorded <code>{value} Litres</code> of water intake for today! ✅'
            elif record_step == 'sleep':
                value = check_sleep(user_input)
                if not value:
                    return await error_message(update, context,
                                               "⛔ Sleep hours must be a number greater than 0. ⛔\n\n↪️ Use this "
                                               "format: <code>8 Hrs</code> to record 8 hours of sleep.")
                msg = f'Successfully recorded <code>{value} Hours</code> of sleep! ✅'
            elif record_step == 'exercise':
                value = check_exercise(user_input)
                if not isinstance(value, int):
                    return await error_message(update, context,
                                               "⛔ Exercise duration must be a number greater than 0. ⛔\n\n↪️ Use this "
                                               "format: <code>30 Minutes</code> to record 30 minutes of exercise.")
                msg = f'Successfully recorded <code>{value} Minutes</code> of exercise for today! ✅'
            table_user_id = await get_user(user_code)
            await enter_record(table_user_id, record_step, value)
            await update.message.reply_html(
                text=msg,
                reply_markup=ReplyKeyboardRemove(),
            )
        elif context.user_data.get('reminder_step'):
            reminder_type = context.user_data.get('reminder_step')
            user_input = update.message.text  # Reminder note
            if reminder_type in ['once', 'repeat']:
                msg = ''
                if reminder_type == 'once':
                    msg = ("🕧 In how much time do you want me to remind you?\n\n<b>Please provide the"
                           "time in minutes:</b>")
                elif reminder_type == 'repeat':
                    msg = ("⏲️ What interval would you like between reminders?\n\n<b>Please provide the"
                           "time in minutes:</b>")
                await update.message.reply_html(text=msg)
                context.user_data['reminder_type'] = reminder_type
                context.user_data['reminder_note'] = user_input
                context.user_data['reminder_step'] = 'due_time'
            elif reminder_type == 'due_time':
                reminder_note = context.user_data.get('reminder_note')
                user_input = update.message.text  # Reminder minutes
                chat_id = update.effective_message.chat_id
                if user_input.isdigit() and int(user_input) > 0:
                    remind_type, note, due_time = (context.user_data['reminder_type'], reminder_note,
                                                   float(user_input) * 60)
                    if remind_type == 'once':
                        context.job_queue.run_once(custom_reminder, due_time, chat_id=chat_id, name=str(user_code),
                                                   data=json.dumps({"due": due_time, "message": note}))
                    elif remind_type == 'repeat':
                        context.job_queue.run_repeating(custom_reminder, due_time, chat_id=chat_id, name=str(user_code),
                                                        data=json.dumps({"due": due_time, "message": note}))
                    await update.message.reply_html(text="🔔 <b>Reminder Set!</b> 🔔"
                                                         f"\n\n<pre>Type: {remind_type.title()}\nNote: {note}"
                                                         f"\nTime: {user_input} Minutes</pre>")
                    context.user_data.clear()
                else:
                    return await error_message(update, context,
                                               "⛔ Reminder minutes must be a number greater than 0. ⛔\n\n↪️ Use this "
                                               "format: <code>30</code> to set a reminder for 30 minutes.")
    except Exception as e:
        log_error(e, 'Failed to handle registration')
        await update.message.reply_html(
            text="An error occurred while processing your request, please try again later. 😢",
        )
