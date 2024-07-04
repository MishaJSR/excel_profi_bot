import os
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from dotenv import find_dotenv, load_dotenv
import logging
import pandas as pd

load_dotenv(find_dotenv())

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Для начала работы введите артикул')

@user_private_router.message(StateFilter('*'))
async def start_cmd(message: types.Message):
    df = await check_table(message)
    if df.empty:
        return
    articul = message.text
    timestamp_columns = df.select_dtypes(include='datetime').columns
    df[timestamp_columns[0]] = df[timestamp_columns[0]].dt.strftime('%d-%m-%Y')
    try:
        index = df[df['Артикул'] == int(articul)].index[0]
        row_data = df.loc[index]
        arguments = list(row_data.values)[1:]
        for index, el in enumerate(arguments):
            await message.answer(f'{df.columns[index + 1]}: {el}')
    except:
        await message.answer('По данному артикулу совпадений не найдено')





async def check_table(message):
    df = pd.DataFrame()
    try:
        df = pd.read_excel('excel_docs/table.xlsx')
    except FileNotFoundError:
        await message.answer(f'Таблица не найдена\nПроверьте наличие файла table.xlsx в папке excel_docs')
    return df