import logging

from random import randint
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    """THE НАЧАЛО"""
    user = update.effective_user
    markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=False)
    await update.message.reply_html(f"Что изволите сделать, господин {user.mention_html()}", reply_markup=markup)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def task(context):
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'Истекло {context.job.data} секунд!')


# Обычный обработчик, как и те, которыми мы пользовались раньше.
async def set_timer(update, context):
    """Добавляем задачу в очередь"""
    time = int(context.args[0])
    markup = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, time, chat_id=chat_id, name=str(chat_id), data=time)

    text = f'Засек {time} секунд!'
    if job_removed:
        text += ' Таймер сброшен.'
    await update.effective_message.reply_text(text, reply_markup=markup)


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    await update.message.reply_text(update.message.text)


async def dice(update, context):
    markup = ReplyKeyboardMarkup(dice_keyboard, one_time_keyboard=False)
    await update.message.reply_text(f"Какой кубик выберете?", reply_markup=markup)


async def d6(update, context):
    await update.message.reply_text(f"Кубик d6: {randint(1, 6)}")


async def d6_2(update, context):
    d1 = randint(1, 6)
    d2 = randint(1, 6)
    await update.message.reply_text(f"Кубик 2d6: {d1}, {d2}\nСумма кубов: {d1 + d2}")


async def d20(update, context):
    await update.message.reply_text(f"Кубик d6: {randint(1, 20)}")


async def timer(update, context):
    markup = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=False)
    await update.message.reply_text(f"Какой кубик выберете?", reply_markup=markup)


async def s30(update, context):
    await update.message.reply_text(f"Кубик d6: {randint(1, 6)}")


async def m1(update, context):
    d1 = randint(1, 6)
    d2 = randint(1, 6)
    await update.message.reply_text(f"Кубик 2d6: {d1}, {d2}\nСумма кубов: {d1 + d2}")


async def m5(update, context):
    await update.message.reply_text(f"Кубик d6: {randint(1, 20)}")


start_keyboard = [['/dice', '/timer']]

timer_keyboard = [['/30s', '/1min'],
                  ['/5min', '/back']]

dice_keyboard = [['/d6', '/2d6'],
                 ['/d20', '/back']]

close_keyboard = [['/close']]


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler(["start", "help", 'back'], start))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("dice", dice))

    application.add_handler(CommandHandler("d6", d6))
    application.add_handler(CommandHandler("2d6", d6_2))
    application.add_handler(CommandHandler("d20", d20))

    application.add_handler(CommandHandler("30s", d6))
    application.add_handler(CommandHandler("1min", d6_2))
    application.add_handler(CommandHandler("5min", d20))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()
