import os
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from dotenv import find_dotenv, load_dotenv
import logging
import pandas as pd
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.user_keyboard import start_kb, col_articul, col_show

load_dotenv(find_dotenv())

user_private_router = Router()

folder_path = '/excel_docs/'


class UserState(StatesGroup):
    start_user = State()
    col_art_choose = State()
    col_show = State()
    user_task = State()
    df = None
    columns_list = None
    col_art = None


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    current_dir = os.getcwd()
    files = os.listdir(current_dir + folder_path)
    df = await check_table(message, current_dir + folder_path + files[0])
    if df.empty:
        return
    else:
        UserState.df = df
        await message.answer('Бот запущен', reply_markup=start_kb())


@user_private_router.message(F.text == 'Указать колонну артикула')
async def fill_admin_state(message: types.Message, state: FSMContext):
    UserState.columns_list = UserState.df.columns.tolist()
    await message.answer('Выберите колонну артикула', reply_markup=col_articul(data=UserState.columns_list))
    await state.set_state(UserState.col_art_choose)


@user_private_router.message(F.text == 'Выбрать отображаемые колонны')
async def fill_admin_state(message: types.Message, state: FSMContext):
    await message.answer('Выберите отображаемые колонны', reply_markup=col_show(data=UserState.columns_list))
    await state.set_state(UserState.col_show)


@user_private_router.message(UserState.col_art_choose, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    UserState.col_art = message.text
    await message.answer(f'Выберана колона артикула: {message.text}', reply_markup=start_kb())


# @user_private_router.message(StateFilter('*'))
# async def start_cmd(message: types.Message):
#     current_dir = os.getcwd()
#     files = os.listdir(current_dir + folder_path)
#     df = await check_table(message, current_dir + folder_path + files[0])
#     if df.empty:
#         return
#     articul = message.text
#     timestamp_columns = df.select_dtypes(include='datetime').columns
#     df[timestamp_columns[0]] = df[timestamp_columns[0]].dt.strftime('%d-%m-%Y')
#     try:
#         print('sds')
#         print(df)
#         index = df[df['Реестровый номер'] == int(articul)].index[0]
#         index_articul = df.columns.get_loc('Реестровый номер')
#         print(index_articul)
#         df = df.drop(columns='Реестровый номер')
#         row_data = df.loc[index]
#         arguments = list(row_data.values)
#         for index, el in enumerate(arguments):
#             await message.answer(f'{df.columns[index]}: {el}')
#     except:
#         await message.answer('По данному артикулу совпадений не найдено')
#
#
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
