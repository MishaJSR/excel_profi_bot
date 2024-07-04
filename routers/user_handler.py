import os
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from dotenv import find_dotenv, load_dotenv
import logging
import pandas as pd

load_dotenv(find_dotenv())

user_private_router = Router()


@user_private_router.message(StateFilter('*'))
async def start_cmd(message: types.Message):
    df = await check_table(message)
    if df.empty:
        return
    articul = message.text
    df['Приход'] = df['Приход'].dt.strftime('%d-%m-%Y %H:%M:%S')
    try:
        index = df[df['Артикул'] == int(articul)].index[0]
        row_data = df.loc[index]
        arguments = list(row_data.values)[1:]
        for el in arguments:
            await message.answer(el)
    except IndexError:
        await message.answer('По данному артикулу совпадений не найдено')





async def check_table(message):
    df = pd.DataFrame()
    try:
        df = pd.read_excel('excel_docs/table.xl')
    except FileNotFoundError:
        await message.answer(f'Таблица не найдена\nПроверьте наличие файла table.xlsx в папке excel_docs')
    return df