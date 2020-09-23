import json
import numpy as np
import random

def get_random_int_seq(max_size:int, seq_size:int):
    """Хелпер для генерации выборки с кастомными параметрами"""
    return np.random.randint(0,max_size, size=(1,seq_size))[0]

def load_json_data_from_file(file_path: str):
    """Читаем json"""
    with open(file_path, "r") as j:
        json_content = json.load(j)
    return json.loads(json_content)

def gen_random_words(number_of_words:int):
    """Главная функция-генератор слов на день и для quiz
       Выбирает рандомные слова и их значения из словаря """
    global j_cont
    seq_random = get_random_int_seq(len(j_cont)-1,number_of_words)
    result = {}
    for index, k in enumerate(j_cont.keys()):
        if index in seq_random:
            result.update({k: j_cont[k]})
    return result

def gen_message_string_with_random_words():
    """Генерим сообщение пользователю с 5 словами для изучения"""
    words_dict = gen_random_words(5)
    mess_string = "<i><b>Words for today:</b></i> &#128214\n\n"
    for k in words_dict.keys():
        mess_string = mess_string + "&#x25B6<u>{}</u>:\n- {}\n\n".format(k,words_dict[k] )
    return mess_string

def gen_quiz():
    """Генерим quiz для пользователя"""
    words_dict = gen_random_words(4)
    write_answer_key = list(words_dict.keys())[0]
    write_answer_value = words_dict[write_answer_key]
    mess_string = "Выберите верное определение <b>'{}'</b>:\n\n".format(write_answer_key)
    quiz_list = [words_dict[k] for k in words_dict.keys()]
    random.shuffle(quiz_list)
    return mess_string, quiz_list, write_answer_value

j_cont=load_json_data_from_file("data/words_with_definitions.json")

if __name__ == "__main__":
    mess_string, l, write_answer_key= gen_quiz()
    print(l)