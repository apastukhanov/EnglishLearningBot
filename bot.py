"""Сервер для бота, запускаем и учим английские слова в Телеге"""
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery

from words_gen import gen_message_string_with_random_words, gen_quiz

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

quiz_controller_dict = {}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветствие и помощь по боту"""
    await message.answer(
        "<u><b>Бот для изучения английских слов</b></u>\n\n"
        "<i>Список доступных команд</i>\n\n"
        "Приcлать 5 рандомных слов: /words\n\n"
        "Начать квиз: /quiz\n\n"
        "Завершить квиз: /stop_quiz\n\n"
        "Помощь по боту: /help\n\n"
        "Запустить бота: /start",
        parse_mode=types.ParseMode.HTML
        )


@dp.message_handler(commands=['words'])
async def send_words(message: types.Message):
    """Отправляем 5 случайный слов выбранных из словаря"""
    words_gen = gen_message_string_with_random_words()
    await message.answer(words_gen, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['stop_quiz'])
async def stop_quiz(message: types.Message):
    """Останавливаем quiz"""
    try:
        if quiz_controller_dict[message.chat.id]["quiz_started"]:
            quiz_controller_dict[message.chat.id]["quiz_started"]=False
            await message.answer("Окей, Quiz остановлен!")
            await print_quiz_results(message)
        else:
            await message.answer("Quiz уже давно не работает &#128579",parse_mode=types.ParseMode.HTML)
    except:
        await message.answer("Quiz еще не запускали... &#128579",parse_mode=types.ParseMode.HTML)
    

@dp.message_handler(commands=['quiz'])
async def start_quiz(message: types.Message):
    """Запускаем счетчики для quiz"""
    quiz_controller_dict.update({
        message.chat.id:
            {"attempt":0,
            "right_ans":0,
            "quiz_started":True}
        })

    await message.answer("<b>Добро пожаловать в квиз!\n"
                    "3..2..1.. Поехали.. </b> 🚀🚀🚀", 
                parse_mode=types.ParseMode.HTML)

    await send_quiz(message)

@dp.message_handler()
async def echo_reply(message: types.Message):
    """Отправляем ответ на неизвестный запрос к бобту"""
    await message.answer(
        "Такая команда недоступна 🤨\n\n"
        "Чтобы получить список команд нажмите /help",
        parse_mode=types.ParseMode.HTML)

@dp.message_handler()
async def send_quiz(message: types.Message):
    """Отправляем quiz"""

    mess_string, quiz_list, write_answer_value = gen_quiz()
    markup = types.InlineKeyboardMarkup()

    right_awnswer = lambda answer_str: "верно" \
    if answer_str == write_answer_value else "не верно"

    for var_btn in quiz_list:
        markup.add(
            types.InlineKeyboardButton(var_btn, 
            callback_data=right_awnswer(var_btn)))

    await message.answer(
        mess_string,
        parse_mode=types.ParseMode.HTML,
        reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'верно')
async def right_answer(callback_query: CallbackQuery):
    """Поздравляем с правильным ответом на вопрос из quiz"""
    try:
        if quiz_controller_dict[callback_query.message.chat.id]["quiz_started"]:
            quiz_controller_dict[callback_query.message.chat.id]["attempt"]+=1
            quiz_controller_dict[callback_query.message.chat.id]["right_ans"]+=1
            
            await bot.send_message(callback_query.from_user.id, 
                                        'Правильно &#127881;&#127881;&#127881;',
                                        parse_mode=types.ParseMode.HTML)

        if quiz_controller_dict[callback_query.message.chat.id]["attempt"] < 5:
            await send_quiz(callback_query.message)
        else:
            await print_quiz_results(callback_query.message)
    except KeyError:
        await start_quiz(callback_query.message)

    
@dp.callback_query_handler(lambda c: c.data == 'не верно')
async def wrong_answer(callback_query: CallbackQuery):
    """Уведомляем об ошибке, если ответ на вопрос из quiz неверный"""
    try:
        if quiz_controller_dict[callback_query.message.chat.id]["quiz_started"]:
            quiz_controller_dict[callback_query.message.chat.id]["attempt"]+=1
            await bot.send_message(callback_query.from_user.id, 
                                'Мимо &#129398&#129398&#129398',
                                parse_mode=types.ParseMode.HTML)

        if quiz_controller_dict[callback_query.message.chat.id]["attempt"] < 5:
            await send_quiz(callback_query.message)
        else:
            await print_quiz_results(callback_query.message)
    except KeyError:
        await start_quiz(callback_query.message)


@dp.callback_query_handler()
async def print_quiz_results(message: types.Message):
    try:
        quiz_controller_dict[message.chat.id]["quiz_started"]=False
        await message.answer(
                            "Окей... на сегодня достаточно &#129299\n\n"
                            "Правильных ответов: <b>{}</b> из <b>{}</b>!\n\n"
                            "<b>Quiz всегда можно пройти заново\n"
                            "просто нажми на /quiz</b>".format(
                                quiz_controller_dict[message.chat.id]["right_ans"],
                                quiz_controller_dict[message.chat.id]["attempt"]),
                                parse_mode=types.ParseMode.HTML)
    except KeyError:
        await message.answer("Упс.. Ваш quiz куда пропал...&#129325")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)