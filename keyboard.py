from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import country_currency_codes

first_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='курс одной единицы валюты'), KeyboardButton(text='своя сумма')]
],
                    resize_keyboard=True)

restart_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Перезапустить бота')]
],
                    resize_keyboard=True)

async def inline_countries(page: int=0):
    keyboard = InlineKeyboardBuilder()
    all_countries = list(country_currency_codes.items())
    items_on_page = 10

    start = page * items_on_page
    end = start + items_on_page
    current = all_countries[start:end]

    for country, code in current:
        keyboard.add(InlineKeyboardButton(text=country, callback_data=code))

    if page > 0:
        keyboard.add(InlineKeyboardButton(text='Предыдущая', callback_data=f'prev_{page}'))
    if end < len(all_countries):
        keyboard.add(InlineKeyboardButton(text='Следующая', callback_data=f'next_{page}'))
    return keyboard.adjust(2).as_markup()

