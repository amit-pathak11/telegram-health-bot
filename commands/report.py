from collections import defaultdict
from datetime import datetime, timedelta

import prettytable as pt
from telegram import Update
from telegram.ext import ContextTypes

from utils.decorators import is_registered
from utils.error_handler import log_error
from utils.helper import get_report


def command():
    @is_registered
    async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            user = update.effective_user
            data = await get_report(user.id)
            if data:
                table = pt.PrettyTable(['DATE', '🥤', '😴', '🤸'])
                table.align['DATE'] = 'l'
                table.align['🥤'] = 'r'
                table.align['😴'] = 'r'
                table.align['🤸'] = 'r'
                grouped_records = defaultdict(dict)
                today = datetime.now()
                start_of_week = today - timedelta(days=today.weekday())
                for record in data:
                    date_str = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S.%f").strftime('%Y-%m-%d')
                    if date_str not in grouped_records:
                        grouped_records[date_str]['DATE'] = date_str
                    grouped_records[date_str][record[1].upper()] = record[2]
                for day in range(7):
                    current_date = start_of_week + timedelta(days=day)
                    date_str = current_date.strftime('%Y-%m-%d')
                    if date_str in grouped_records:
                        record = grouped_records[date_str]
                        table.add_row([record.get('DATE', ''), record.get('WATER', ''), record.get('SLEEP', ''),
                                       record.get('EXERCISE', '')])
                    else:
                        table.add_row([date_str, '', '', ''])
                await update.message.reply_html(
                    f'Welcome back {user.mention_html()}!\nHere is your weekly health report. 📊'
                    f'\n<pre>\n{table}\n</pre>')
            else:
                await update.message.reply_html(f"Sadly, you don't have any records for\nthis week. 😥"
                                                f"\n\nWhat are you waiting for? Send /record and "
                                                f"start tracking your health. 📑")
        except Exception as e:
            log_error(e, 'Failed to register user')
            await update.message.reply_html(
                text="An error occurred while processing your request, please try again later. 😢",
            )

    return report
