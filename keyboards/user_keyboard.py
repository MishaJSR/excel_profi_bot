from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_but = ['Вписать артикул', 'Указать колонну артикула', 'Выбрать отображаемые колонны']


def start_kb(data=None):
    test_kb = ReplyKeyboardBuilder()
    for el in start_but:
        test_kb.button(text=el)
    test_kb.adjust(1, 1)
    return test_kb.as_markup(resize_keyboard=True)

def col_articul(data=None):
    test_kb = ReplyKeyboardBuilder()
    test_kb.button(text='Вернуться')
    for el in data:
        test_kb.button(text=el)
    test_kb.adjust(1, 1)
    return test_kb.as_markup(resize_keyboard=True)

def col_show(data=None):
    test_kb = ReplyKeyboardBuilder()
    test_kb.button(text='Вернуться')
    for el in data:
        test_kb.button(text=el)
    test_kb.adjust(1, 1)
    return test_kb.as_markup(resize_keyboard=True)