"""**************************************************ГЕНЕРИРУЕМ КЛАВИАТУРУ**************************************************"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


LEXICON: dict[str, str] = {
    'button_skills_pressed': 'Ключевые навыки \U0001F6E0',
    'button_words_pressed': 'Слова в описании \U0001F4CB',
    'button_salary_rur_pressed': 'З/П в рублях \U0001F1F7\U0001F1FA',
    'button_salary_usd_pressed': 'З/П в долларах \U0001F1FA\U0001F1F8'}


# Функция для генерации инлайн-клавиатур 
def create_inline_kb(width: int, *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()
