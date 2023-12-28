import json
import os
import re
from datetime import datetime, timedelta, date
from typing import Union

import aiosqlite
from PIL import Image, ImageDraw, ImageFont
from telegram.ext import ContextTypes

import settings

db_file_path = os.path.join(settings.DATA_DIRECTORY_PATH, 'database', 'data.db')


def check_gender(gender) -> bool:
    return gender in ['Male 👨🏻', 'Female 👩🏻']


def check_age(age) -> bool:
    return str(age).isdigit() and 18 <= int(age) <= 100


def check_name(name) -> bool:
    """ Check if the name contains only letters """
    return name.isalpha() and len(name) >= 3


def check_water(water) -> Union[int, bool]:
    get_water = re.search(r'(\d+)\s?L?', water, re.IGNORECASE)
    if get_water:
        litres = int(get_water.group(1))
        if litres > 0:
            return litres
    return False


def check_sleep(sleep) -> Union[int, bool]:
    get_sleep = re.search(r'(\d+)\s?(?:Hrs)?', sleep, re.IGNORECASE)
    if get_sleep:
        hrs = int(get_sleep.group(1))
        if hrs > 0:
            return hrs
    return False


def check_exercise(exercise) -> Union[int, bool]:
    get_exercise = re.search(r'(\d+)\s?(?:Minutes)?', exercise, re.IGNORECASE)
    if get_exercise:
        minutes = int(get_exercise.group(1))
        if minutes >= 0:
            return minutes
    return False


async def register_user(user_code, name, gender, age) -> None:
    """ Register user to the database """
    db = await aiosqlite.connect(db_file_path)
    await db.execute('INSERT INTO users (user_id, name, gender, age) VALUES (?, ?, ?, ?)',
                     (user_code, name, gender, age))
    await db.commit()
    await db.close()


async def check_cooldown(user_code, record_type) -> tuple[bool, str]:
    """ Check the cooldown for given type for the user """

    record_id = await get_user(user_code)
    db = await aiosqlite.connect(db_file_path)
    cursor = await db.execute(
        'SELECT datetime FROM records WHERE user_id = (?) AND type = (?) ORDER BY record_id DESC LIMIT 1',
        (record_id, record_type,))
    last_record = await cursor.fetchone()
    if not last_record:
        return True, 'NO RECORDS'

    recoded = datetime.strptime(last_record[0], '%Y-%m-%d %H:%M:%S.%f')
    current_ts = datetime.now()
    next_record = recoded + timedelta(hours=24)
    if current_ts >= next_record:
        return True, 'NO COOLDOWN'

    remain = next_record - current_ts
    hours, seconds = divmod(remain.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return False, f'{hours}h {minutes}m {seconds}s'


async def get_user(user_code) -> Union[None, int]:
    db = await aiosqlite.connect(db_file_path)
    cursor = await db.execute('SELECT id from users WHERE user_id = ?', (user_code,))
    uid = await cursor.fetchone()
    await db.close()
    if not uid:
        return None
    return int(uid[0])


async def enter_record(user_id, record_type, value) -> None:
    db = await aiosqlite.connect(db_file_path)
    cur_time = datetime.now()
    await db.execute('INSERT INTO records (user_id, type, value, datetime) VALUES (?, ?, ?, ?)',
                     (user_id, record_type, value, cur_time))
    await db.commit()
    await db.close()


async def get_report(user_code):
    record_id = await get_user(user_code)
    db = await aiosqlite.connect(db_file_path)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    cursor = await db.execute(
        'SELECT datetime, type, value FROM records WHERE user_id = ? AND datetime BETWEEN ? AND ?'
        'ORDER BY datetime DESC LIMIT 7', (record_id, start_of_week, end_of_week)
    )
    records = await cursor.fetchall()
    return records


async def custom_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    json_data = json.loads(job.data)
    await context.bot.send_message(chat_id=job.chat_id,
                                   text=f"⏰ <b>Your Custom Reminder</b>\n\n"
                                        f"🗒️ Note:\n<pre>{json_data['message']}</pre>",
                                   parse_mode='HTML'
                                   )


async def get_health_card(user_code, pfp) -> str:
    record_id = await get_user(user_code)
    image_file_path = os.path.join(settings.DATA_DIRECTORY_PATH, 'images', 'health_cards', f'{user_code}.png')
    img = Image.open(os.path.join(settings.DATA_DIRECTORY_PATH, 'images', 'card.png'))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(settings.DATA_DIRECTORY_PATH, 'fonts', f'roboto.ttf'), 17)

    db = await aiosqlite.connect(db_file_path)
    cursor = await db.execute('SELECT name, age, gender FROM users WHERE user_id = ?', (user_code,))
    name, age, gender = await cursor.fetchone()
    cursor = await db.execute('SELECT * FROM records WHERE user_id = ?', (record_id,))
    records = await cursor.fetchall()
    if records:
        record_count = len(records)
        cursor = await db.execute(
            'SELECT datetime FROM records WHERE user_id = ?'
            'ORDER BY datetime DESC LIMIT 1', (record_id,)
        )
        last_record = await cursor.fetchone()
        record_date = datetime.strptime(last_record[0], "%Y-%m-%d %H:%M:%S.%f").strftime('%Y-%m-%d')
    else:
        record_date = "N/A"
        record_count = 0

    # Card information process
    draw.text((215, 83), str(name), (0, 0, 0), font=font)
    draw.text((200, 112), str(age), (0, 0, 0), font=font)
    draw.text((223, 140), str(gender), (0, 0, 0), font=font)
    draw.text((276, 168), f"{record_count} Entries", (0, 0, 0), font=font)
    draw.text((276, 195), str(record_date), (0, 0, 0), font=font)

    # ID process
    draw.text((200, 265), str(user_code), (0, 0, 0), font=font)

    # Card profile picture process
    im = Image.open(pfp)
    width, height = 110, 110
    im = im.resize((width, height), Image.LANCZOS)
    img.paste(im, (20, 95))
    img.save(image_file_path)
    return image_file_path
