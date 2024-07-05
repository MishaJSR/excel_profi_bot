import os
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from dotenv import find_dotenv, load_dotenv
import logging
import pandas as pd
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.user_keyboard import start_kb, col_articul, col_show, correct, back_kb

load_dotenv(find_dotenv())

user_private_router = Router()

folder_path = '/excel_docs/'


class UserState(StatesGroup):
    start_user = State()
    col_art_choose = State()
    col_show = State()
    success_show = State()
    set_articul = State()
    df = None
    columns_list = None
    col_art = None
    col_to_show = []
    col_to_show_pool = []
    pool_str = None


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
    await message.answer('Главное меню', reply_markup=start_kb())
    await state.set_state(UserState.start_user)

@user_private_router.message(StateFilter('*'), F.text == 'Сбросить настройки')
async def fill_admin_state(message: types.Message, state: FSMContext):
    UserState.df = None
    UserState.col_art = None
    UserState.col_to_show = []
    UserState.col_to_show_pool = []
    UserState.pool_str = None
    await message.answer('Настройки сброшены', reply_markup=start_kb())
    await state.set_state(UserState.start_user)



@user_private_router.message(StateFilter('*'), F.text == 'Указать колонну артикула')
async def fill_admin_state(message: types.Message, state: FSMContext):
    await message.answer('Выберите колонну артикула', reply_markup=col_articul(data=UserState.columns_list))
    await state.set_state(UserState.col_art_choose)

@user_private_router.message(UserState.col_art_choose, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    UserState.col_art = message.text
    await message.answer(f'Выберана колона артикула: {message.text}', reply_markup=start_kb())
    await state.set_state(UserState.start_user)






@user_private_router.message(StateFilter('*'), F.text == 'Выбрать отображаемые колонны')
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


@user_private_router.message(StateFilter('*'), F.text == 'Перейти далее')
async def fill_admin_state(message: types.Message, state: FSMContext):
    await message.answer('Вводите артикулы', reply_markup=back_kb())
    await state.set_state(UserState.set_articul)



@user_private_router.message(UserState.set_articul, F.text)
async def start_subj_choose(message: types.Message, state: FSMContext):
    articul = message.text
    if message.text.isdigit():
        articul = int(articul)
    try:
        col_to_show_pool = [UserState.columns_list.index(el) for el in UserState.col_to_show]

        df_filtered = UserState.df[UserState.df[UserState.col_art] == articul]
        df_filtered = df_filtered.iloc[:, col_to_show_pool]
        list_col_to_index = df_filtered.columns.tolist()
        list_col_to_index = [x.strip() for x in list_col_to_index]
        arguments = list(df_filtered.values)
        text_to_answer = ''
        for name, el in zip(list_col_to_index, arguments):
            print(name)
            print(el)
            #await message.answer(f'{df_filtered.columns[index]}: {el}\n')
    except Exception as e:

        print(e)
        await message.answer('По данному артикулу совпадений не найдено')



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
