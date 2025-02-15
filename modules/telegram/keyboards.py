import json

from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def start():
    async with open("modules/telegram/data/config.json", encoding="utf-8") as f:
        data = json.load(f)

    keyboard = ReplyKeyboardBuilder()
    button = [KeyboardButton(text=item) for item in data]
    keyboard.add(*button)

    return keyboard.adjust(3).as_markup()
