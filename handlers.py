"""**************************************************ОСНОВНАЯ ЛОГИКА БОТА**************************************************"""
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
#-----------------------------------------------------------
import requests
import lxml
import pandas as pd
import json
from bs4 import BeautifulSoup

from made_list import normalize, sort
from keyboard import create_inline_kb
from keyboard import LEXICON


# Функция, извлекающая всю информацию в формате json из всех полученных вакансий 
def get_vacancyes(text: str):
    params = {
            "per_page": 30,
            "page": 0,
            "period": 30,
            "text": text
            }
    res = requests.get("https://api.hh.ru/vacancies", params = params)
    
    vacancies = res.json()

    all_vacancies = []
    
    for i in vacancies['items']:
        get_id = i['id']
        get_info = requests.get(f'https://api.hh.ru/vacancies/{get_id}')
        all_vacancies.append(get_info.json())
        
    return all_vacancies

#---------------------------------------------------------------------------------

# Здесь получаем текст описания вакансий
def get_text(arg):
    vacancy_df = pd.DataFrame(arg)
    itog = vacancy_df['description']
    words: str = ''

    for j in itog:
        soup = BeautifulSoup(j, 'lxml')
        text = soup.text
        words = f'{words} {text}'
    
    return words
   

# Здесь получаем перечень ключевых навыков в вакансиях
def get_skills(arg):
    all_skils = []
    for vacancy in arg:
        for skill in vacancy['key_skills']:
            all_skils.append(skill['name'])
                                   
    return all_skils                    
   

# ------------------- Блок генерации средних зарплат в RUR ------------------- 
def salary_ru(arg):
    salary_from = [i['salary']['from'] for i in arg if i['salary'] and
          isinstance(i['salary']['from'], int) and i['salary']['currency'] == 'RUR']

    salary_to = [i['salary']['to'] for i in arg if i['salary'] and
          isinstance(i['salary']['to'], int) and i['salary']['currency'] == 'RUR']

    for item_ru in arg:
        if item_ru['salary'] and item_ru['salary']['currency'] == 'RUR':
            currency_ru = item_ru['salary']['currency']
        
    salary_sum_from_ru = int(sum(salary_from) / len(salary_from))
    salary_sum_to_ru = int(sum(salary_to) / len(salary_to))

    return f'от {salary_sum_from_ru} до {salary_sum_to_ru} {currency_ru}'


# ------------------- Блок генерации средних зарплат в USD -------------------
def salary_us(arg_us):
    salary_from_us = [i['salary']['from'] for i in arg_us if i['salary'] and
      isinstance(i['salary']['from'], int) and i['salary']['currency'] == 'USD']

    salary_to_us = [i['salary']['to'] for i in arg_us if i['salary'] and
      isinstance(i['salary']['to'], int) and i['salary']['currency'] == 'USD']

    for item_us in arg_us:
        if item_us['salary'] and item_us['salary']['currency'] == 'USD':
            currency_us = item_us['salary']['currency']
    
    salary_sum_from_us = int(sum(salary_from_us))
    salary_sum_to_us = int(sum(salary_to_us))

    if salary_sum_from_us != 0 and salary_sum_to_us != 0:               # Проверка на наличие в полученном словари зарплат в USD
        salary_from_usd = salary_sum_from_us // len(salary_from_us)
        salary_to_usd = salary_sum_to_us // len(salary_to_us)
        
        return f'от {salary_from_usd} до {salary_to_usd} {currency_us}'

    elif salary_sum_from_us == 0 and salary_sum_to_us == 0:
        return f'\n\nВ этой сфере работодатели пока платят только рублями \U0001F644'

    else:
        return f'от {salary_sum_from_us} {currency_us}'

# ------------------- Блок пользовательских хэндлеров -------------------

router: Router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nЯ помогу тебе понять,\nчто больше всего интересует работодателей в выбранной профессии.'
                         '\nЧто бы узнать подробнее воспользуйся\n /help')


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer('''Что бы узнать, какие ключевые навыки чаще всего указывают работодатели,
\nа так же, какие слова чаще всего они используют в описании \nпросто напиши мне название интересующей профессии.
\nНапример "повар" (без кавычек). \nЯ собираю статистику по сотням вакансий
на самом популярном сервисе по поиску работы <b>hh</b>. \nТы сможешь увидеть\U0001F440: \n\U0001F538топ ключевых навыков
\n\U0001F538топ самых популярных слов в описании
\n\U0001F538ну и конечно среднии зарплаты по рынку в этой профессии! \n\nНу что, погнали?\U0001F3C4''')


# Этот хэндлер будет срабатывать на любые текстовые сообщения,
# кроме команд "/start" и "/help"
@router.message()
async def send_echo(message: Message):
    try:
        await message.answer(text='\U0001F575')
        await message.answer(text='Собираю информацию\nНужно немного подождать...')

        global profession
        profession = message.text
        
        content = get_vacancyes(profession)

        skills = get_skills(content)
        global sorted_skills
        sorted_skills = sort(skills)

        content_text = get_text(get_vacancyes(profession))
        normalize_text = normalize(content_text)

        global sorted_text
        sorted_text = sort(normalize_text)

        global salary_rur
        salary_rur = salary_ru(content)

        global salary_usd
        salary_usd = salary_us(content)

        # Отправляем клавиатуру пользователю
        
        keyboard = create_inline_kb(2, 'button_skills_pressed', 'button_words_pressed',
                                  'button_salary_rur_pressed', 'button_salary_usd_pressed')

        await message.answer(text='Нашёл кое-что интересное, \nможно глянуть \U0001F447',
                                 reply_markup=keyboard)
    except ValueError:
        await message.answer(text='Похоже такой профессии ещё не придумали,\nвозможно ты будешь в ней первым! \U0001F60E')
    except ZeroDivisionError:
        await message.answer(text='Что то пошло не так \U0001F974 \nпопробуй ещё раз')
    except KeyError:
        await message.answer(text='Я немного устал\U0001F915 \nДай мне отдохнуть какое то время и я снова буду готов к работе!')
    except TypeError:
        await message.answer(text='Что то пошло не так \U0001F974 \nпопробуй ещё раз')
        
        
# ------------------- Блок обработки инлайн-кнопок -------------------

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_skills_pressed'
@router.callback_query(Text(text=['button_skills_pressed']))
async def process_button_skills(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
        text = f'\U0001F534 <b>Рейтинг ключевых навыков \nпо вакансии {profession}:</b> \n{sorted_skills}',
        reply_markup=callback.message.reply_markup)
    except TelegramBadRequest:
        await callback.answer()


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_words_pressed'
@router.callback_query(Text(text=['button_words_pressed']))
async def process_button_words(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
        text=f'\U0001F534 <b>Рейтинг часто встречающихся\nслов в описании:</b> \n{sorted_text}',
        reply_markup=callback.message.reply_markup)
    except TelegramBadRequest:
        await callback.answer()


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_salary_rur_pressed'
@router.callback_query(Text(text=['button_salary_rur_pressed']))
async def process_button_salary_rur(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
        text=f'<b>Средняя зарплата: {salary_rur}</b>',
        reply_markup=callback.message.reply_markup)
    except TelegramBadRequest:
        await callback.answer()


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_salary_usd_pressed'
@router.callback_query(Text(text=['button_salary_usd_pressed']))
async def process_button_salary_usd(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
        text=f'<b>Средняя зарплата USD: {salary_usd}</b>',
        reply_markup=callback.message.reply_markup)
    except TelegramBadRequest:
        await callback.answer()
    
    


    
    


    




