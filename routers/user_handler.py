import os
from aiogram import types, Router, F
from dotenv import find_dotenv, load_dotenv
import logging

load_dotenv(find_dotenv())

user_private_router = Router()


def filter_message(text):
    if 'вы привязали к своему личному кабинету номер' in text.lower():
        return True
    elif 'закрытие с выдачей наличных' in text.lower():
        return True
    elif 'карта заблокирована' in text.lower():
        return True
    elif 'подтверждение номера телефона' in text.lower():
        return True
    elif 'подтвердите обслуживание в офисе. введите код' in text.lower() and \
            'на устройстве сотрудника. никому его не сообщайте' in text.lower():
        return True
    elif 'для подписания чека выдачи наличных на' in text.lower() and \
            ' введите код' in text.lower() and \
            'на устройстве сотрудника. никому его не сообщайте' in text.lower():
        return True
    return False


@user_private_router.channel_post()
async def message_in_group(message: types.Message):
    logging.info('get message')
    if filter_message(message.text):
        logging.info('filter message')
        await message.bot.send_message(chat_id=os.getenv('CHAT_ID_RESIEVER'), text='⚠⚠⚠' + message.text + '⚠⚠⚠')
        await message.bot.send_message(chat_id=os.getenv('CHAT_ID_RESIEVER'), text='⚠⚠⚠' + message.text + '⚠⚠⚠')
        await message.bot.send_message(chat_id=os.getenv('CHAT_ID_RESIEVER'), text='⚠⚠⚠' + message.text + '⚠⚠⚠')
        await message.bot.send_message(chat_id=os.getenv('CHAT_ID_RESIEVER'), text='⚠⚠⚠' + message.text + '⚠⚠⚠')
