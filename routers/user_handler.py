import os
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from dotenv import find_dotenv, load_dotenv
import logging
import datetime
import pandas as pd
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import re

from keyboards.user_keyboard import start_kb, col_articul, col_show, correct, back_kb, art_ch

load_dotenv(find_dotenv())

user_private_router = Router()

folder_path = '/excel_docs/'


class UserState(StatesGroup):
    start_user = State()
    col_art_choose = State()
    col_show = State()
    success_show = State()
    set_articul = State()
    ready_set_articul = State()
    set_to_articul = State()
    set_articul_one = State()
    df = None
    columns_list = None
    col_art = None
    col_to_show = []
    col_to_show_pool = []
    pool_str = None
    df_filtered = None
    num_of_rows = None


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    current_dir = os.getcwd()
    files = os.listdir(current_dir + folder_path)
    df = await check_table(message, current_dir + folder_path + files[0])
    if df.empty:
        return
    else:
        UserState.df = df
        UserState.columns_list = UserState.df.columns.tolist()
        UserState.columns_list = [x.strip() for x in UserState.columns_list]
        await message.answer('Бот запущен', reply_markup=start_kb())

@user_private_router.message(StateFilter('*'), F.text == 'Вернуться')
async def fill_admin_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == UserState.set_articul_one:
        await state.set_state(UserState.set_articul)
        await message.answer('Вводите артикул', reply_markup=back_kb())
    else:
        await message.answer('Главное меню', reply_markup=start_kb())
        await state.set_state(UserState.start_user)




@user_private_router.message(StateFilter('*'), F.text == 'Указать колонну артикула')
async def fill_admin_state(message: types.Message, state: FSMContext):
    await message.answer('Выберите колонну артикула', reply_markup=col_articul(data=UserState.columns_list))
    await state.set_state(UserState.col_art_choose)

@user_private_router.message(UserState.col_art_choose, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    UserState.col_art = message.text
    await message.answer(f'Выберана колона артикула: {message.text}', reply_markup=start_kb())
    await state.set_state(UserState.set_to_articul)



@user_private_router.message(UserState.set_to_articul)
async def fill_admin_state(message: types.Message, state: FSMContext):
    UserState.col_to_show = []
    UserState.pool_str = []
    UserState.col_to_show_pool = UserState.columns_list.copy()
    await message.answer('Выберите отображаемые колонны', reply_markup=col_show(data=UserState.col_to_show_pool))
    await state.set_state(UserState.col_show)

@user_private_router.message(UserState.col_show, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    if message.text == 'Готово':
        UserState.pool_str = 'Выбранные поля:\n'
        for el in UserState.col_to_show:
            UserState.pool_str += el + '\n'
        await message.answer(UserState.pool_str, reply_markup=start_kb())
        await state.set_state(UserState.start_user)
        return
    UserState.col_to_show_pool.remove(message.text)
    UserState.col_to_show.append(message.text)
    await message.answer(f'Продолжите выбор или нажмите кнопку Готово', reply_markup=col_show(data=UserState.col_to_show_pool))




@user_private_router.message(StateFilter('*'), F.text == 'Вписать артикул')
async def fill_admin_state(message: types.Message, state: FSMContext):
    if not UserState.col_art or not UserState.pool_str:
        await message.answer('Параметры не заданы')
        return
    await message.answer(f'*Поле артикула*:  {UserState.col_art}\n\n*Выбранные поля*{UserState.pool_str[14:]}', parse_mode="Markdown")
    await message.answer('Все верно?', reply_markup=correct())
    await state.set_state(UserState.ready_set_articul)


@user_private_router.message(UserState.ready_set_articul)
async def fill_admin_state(message: types.Message, state: FSMContext):
    await message.answer('Вводите артикул', reply_markup=back_kb())
    await state.set_state(UserState.set_articul)


@user_private_router.message(UserState.set_articul, F.text)
async def fill_admin_state(message: types.Message, state: FSMContext):
    UserState.num_of_rows = None
    UserState.df_filtered = None
    articul = message.text
    text_to_show = ''
    if message.text.isdigit():
        articul = int(articul)
    try:
        type_col = UserState.df.dtypes[UserState.col_art]
        if type_col.name == 'float64':
            articul = float(articul)
        pattern = r'\d{2}.\d{2}.\d{4}'
        if re.match(pattern, str(articul)):
            print(f'Text "{articul}" соответствует формату даты "dd.mm.yyyy"')
            year = int(articul[6:])
            month = int(articul[3:5])
            day = int(articul[:2])
            print(year, month, day)
            articul = datetime.datetime(year=year, month=month, day=day)

        col_to_show_pool = [UserState.columns_list.index(el) for el in UserState.col_to_show]
        df_filtered = UserState.df[UserState.df[UserState.col_art] == articul]
        UserState.df_filtered = df_filtered.iloc[:, col_to_show_pool]
        UserState.num_of_rows = df_filtered.shape[0]
        if UserState.num_of_rows == 1:
            await state.set_state(UserState.set_articul)
            await one_exeption(message, state)
        else:
            for ind in range(UserState.num_of_rows):
                text_to_show += f'{ind + 1}) '
                for column in UserState.df_filtered.columns:
                    value = UserState.df_filtered[column].iloc[ind]
                    if isinstance(value, datetime.datetime):
                        value = value.strftime('%d.%m.%Y')
                    if isinstance(value, float):
                        value = str(value)[:-2]
                    text_to_show += f"*{column}*: {value}\n"
                text_to_show += '\n'
            await message.answer(text_to_show, parse_mode="Markdown")
            await message.answer('Выберите необходимый артикул', reply_markup=art_ch(data=UserState.num_of_rows))
            await state.set_state(UserState.set_articul_one)
    except:
        await message.answer('По данному артикулу совпадений не найдено')




@user_private_router.message(UserState.set_articul_one, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    text_to_show = ''
    if not message.text.isdigit():
        await message.answer('Ошибка ввода')
        await state.set_state(UserState.set_articul)
        await message.answer('Введите правильный артикул')
        return
    position = int(message.text) - 1
    one_series = UserState.df_filtered.iloc[position]
    for key, value in one_series.items():
        if isinstance(value, datetime.datetime):
            value = value.strftime('%d.%m.%Y')
        if isinstance(value, float):
            value = str(value)[:-2]
        text_to_show += f"*{key}*: {value}\n"
    await message.answer(text_to_show, parse_mode="Markdown")


async def one_exeption(message, state):
    text_to_show = ''
    position = 0
    one_series = UserState.df_filtered.iloc[position]
    for key, value in one_series.items():
        if isinstance(value, datetime.datetime):
            value = value.strftime('%d.%m.%Y')
        if isinstance(value, float):
            value = str(value)[:-2]
        text_to_show += f"*{key}*: {value}\n"
    await message.answer(text_to_show, parse_mode="Markdown")
    await message.answer('Можете вводить следующий артикул')



#
#
#
async def check_table(message, path):
    df = pd.DataFrame()
    try:
        df = pd.read_excel(path)
    except FileNotFoundError:
        await message.answer(f'Таблица не найдена\nПроверьте наличие файла table.xlsx в папке excel_docs')
    return df
