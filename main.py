import logging
from typing import Any

from telegram import Update, InputTextMessageContent, InlineQueryResultArticle
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import tracemalloc
import asyncio

from tools import get_apod, find_picture_by_date, get_time

tracemalloc.start()
picture = ""

APP_TOKEN = "5729584321:AAGWK8f1-yQkrW1u2J1NLT9frFpex09NmrI"
application = ApplicationBuilder().token(APP_TOKEN).build()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

chat_ids_list: list[Any] = []
my_chat_id = 453256411


async def put_in_users(update, context):
    if (update.message.chat.id not in chat_ids_list):
        chat_ids_list.append(update.message.chat.id)
        f = open('chat_IDS.dat', 'a')
        f.write(str(get_time() + "\t" + str(update.message.chat.id) + "\t" + str(update)) + '\n')
        f.close()
        await context.bot.send_message(
            chat_id=my_chat_id,
            text="Новый пользователь с момента перезапуска " + str(update.message.chat.id) + " " +
                 update.message.chat.username + "\n Текущий список чатов: \n" + str(chat_ids_list)
        )
    await asyncio.sleep(2)
    print(chat_ids_list)


def logging_message(update, filename):
    f = open(filename + ".dat", 'a')
    f.write(get_time() + "\t" + str(update.message.text) + "\t" + str(update.message) + '\n')
    f.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await put_in_users(update, context)
    logging_message(update, 'started_chats')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет, сейчас я умею работать только с одной командой"
             "/get_today_picture и я покажу тебе лучшую картинку текущего дня. "
             "Но ещё я могу найти Космическую картинку дня из кое-каких архивов\n"
             "Архив ведется с первого января 2015 года\n"
             ""
             "Попробуй ввести дату в следующем формате ДД ММ ГГ, "
             "а я попробую что-нибудь нарыть. "
             "Я буду смотреть только на первые шесть введённых цифр - не забудь нули, пожалуйста. "
             "Можешь использовать любые разделители, или не использовать их вовсе - так даже интереснее)\n"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="А планы развития у меня следующие: \n"
             "Хочу научиться показывать тебе сразу 10 совершенно случайных космических картинок"
             "\nСейчас я показываю картинку дня только по запросу - однако человеки стали забывать о космосе. "
             "Я стану напоминать тебе каждый день, что космос достаточно близок")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        picture = find_picture_by_date(update.message.text)

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=picture.url)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=picture.name + "\n\n" + picture.description)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=str(e))
        logging_message(update, 'err')


async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        picture = get_apod()
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=picture.url)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=picture.name + "\n\n" + picture.description)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=str(e))
        print(get_apod())
        f = open("err.dat", 'a')
        f.write(update.message.text + '\n')
        f.close()


if __name__ == '__main__':
    application = ApplicationBuilder().token(APP_TOKEN).build()
    handlers = [
        CommandHandler('start', start),
        CommandHandler('get_today_picture', get),
        CommandHandler('info', info),
        MessageHandler(filters.ALL & (~filters.COMMAND), echo)
    ]

    for handler in handlers:
        application.add_handler(handler)
    application.run_polling()
