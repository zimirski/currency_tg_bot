from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


import currencyapicom


import keyboard as kb
import config

router = Router()
currency = currencyapicom.Client(config.api_key)


class ChoiceCountry(StatesGroup):
    country1 = State()
    country2 = State()

class SaveSumm(StatesGroup):
    summ = State()

@router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(text='Здравствуйте, выберите способ конвертации', reply_markup=kb.first_choice)

@router.message(F.text == 'своя сумма')
async def write_your_sum(message: Message, state: FSMContext):
    await message.answer(text='Введите вашу сумму', reply_markup=kb.restart_button)
    await state.set_state(SaveSumm.summ)

@router.message(SaveSumm.summ)
async def check_int(message: Message, state: FSMContext):
    if message.text == 'Перезапустить бота':
        await start_message(message)
        return
    try:
        summ = float(message.text.replace(',', '.'))

        if summ <= 0:
            await message.answer('Сумма не должна быть меньше нуля')
            return

        await state.update_data(summ=summ)
        await message.reply(text='Выберите интересующую вас страну', reply_markup= await kb.inline_countries())
        await state.set_state(ChoiceCountry.country1)

    except ValueError:
        await message.answer(text='Вы ввели некорректную цифру. Повторите попытку')

@router.message(F.text == 'курс одной единицы валюты')
async def one_unit_rate(message: Message, state: FSMContext):
    await state.update_data(summ=1.0)
    await message.reply(text='Выберите интересующую вас страну', reply_markup= await kb.inline_countries())
    await message.answer(text='Используйте кнопку ниже для перезапуска', reply_markup=kb.restart_button)
    await state.set_state(ChoiceCountry.country1)


@router.callback_query(F.data.startswith('prev') | F.data.startswith('next'))
async def pagination(callback: CallbackQuery):
    action, page = callback.data.split('_')
    page = int(page)

    if action == 'prev':
        new_page = page - 1
    else:
        new_page = page + 1

    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_countries(new_page)
    )
    await callback.answer()

@router.callback_query(ChoiceCountry.country1, F.data.in_(kb.country_currency_codes.values()))
async def first_country(callback: CallbackQuery, state: FSMContext):
    await state.update_data(country1 = callback.data)
    await state.set_state(ChoiceCountry.country2)
    await callback.message.edit_text(
        "Выберите страну в валюту которого вы хотите конвертировать",
        reply_markup=await kb.inline_countries()
    )
    await callback.answer(f'Вы выбрали {callback.data}')

@router.callback_query(ChoiceCountry.country2, F.data.in_(kb.country_currency_codes.values()))
async def handle_second_country(callback: CallbackQuery, state: FSMContext):
    await state.update_data(country2=callback.data)
    data = await state.get_data()
    try:
        result = currency.latest(base_currency=data['country1'], currencies=[data['country2']])
        await callback.message.answer(f'{data['summ']} {data['country1']} равен {round((result['data'][data['country2']]['value']*data['summ']),4)} {data['country2']}')
    except ValueError:
        await callback.message.answer('Нет такой конвертации, выберите заново валютную пару')
    await state.clear()
    await callback.answer(f'Вы выбрали {callback.data}')

@router.message(F.text == 'Перезапустить бота')
async def restart_bot(message: Message):
    await start_message(message)



