"""Сервер Telegram бота, запускаемый непосредственно"""
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
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для изучения английских слов\n\n"
        "Приcлать 5 рандомных слов: /words\n\n"
        "Начать квиз: /quiz\n\n"
        "Завершить квиз: /stop_quiz\n\n"
        )


@dp.message_handler(commands=['words'])
async def send_words(message: types.Message):
    """Отправляет 5 слов"""
    words_gen = gen_message_string_with_random_words()
    await message.answer(words_gen, parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['stop_quiz'])
async def stop_quiz(message: types.Message):
    """Останавливаем quiz"""
    await message.answer("Окей! Квиз остановлен!")

@dp.message_handler(commands=['quiz'])
async def start_quiz(message: types.Message):
    """Отправляет предложение пройти квиз"""
    quiz_controller_dict.update({message.chat.id:{"attempt":0,"right_ans":0}})
    await send_quiz(message)

@dp.message_handler(commands=['quiz2'])
async def send_quiz(message: types.Message):   
    mess_string, quiz_list, write_answer_value = gen_quiz()
    markup = types.InlineKeyboardMarkup()
    right_awnswer = lambda answer_str: "верно" if answer_str == write_answer_value else "не верно"

    for var_btn in quiz_list:
        markup.add(types.InlineKeyboardButton(var_btn, callback_data=right_awnswer(var_btn)))

    await message.answer(mess_string,parse_mode=types.ParseMode.HTML,reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == 'верно')
async def right_answer(callback_query: CallbackQuery):

    if quiz_controller_dict[callback_query.message.chat.id]["attempt"] < 5:
        quiz_controller_dict[callback_query.message.chat.id]["right_ans"]+=1
        #await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Right answer &#127881;&#127881;&#127881;',parse_mode=types.ParseMode.HTML)
        await send_quiz(callback_query.message)
    else:
        await bot.send_message(callback_query.from_user.id, 'Right answer &#127881;&#127881;&#127881;',parse_mode=types.ParseMode.HTML)
        await bot.send_message(callback_query.from_user.id,"Окей... на сегодня достаточно!\n\nПравильных ответов {} из 5!".format(quiz_controller_dict[callback_query.message.chat.id]["right_ans"]))
    quiz_controller_dict[callback_query.message.chat.id]["attempt"]+=1

@dp.callback_query_handler(lambda c: c.data == 'не верно')
async def wrong_answer(callback_query: CallbackQuery):

    if quiz_controller_dict[callback_query.message.chat.id]["attempt"] < 5:
        #await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Wrong answer &#9785;',parse_mode=types.ParseMode.HTML)
        await send_quiz(callback_query.message)
    else:
        await bot.send_message(callback_query.from_user.id, 'Wrong answer &#9785;',parse_mode=types.ParseMode.HTML)
        await bot.send_message(callback_query.from_user.id,"Окей... на сегодня достаточно!\n\nПравильных ответов: {} из 5!".format(quiz_controller_dict[callback_query.message.chat.id]["right_ans"]))
    quiz_controller_dict[callback_query.message.chat.id]["attempt"]+=1

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)