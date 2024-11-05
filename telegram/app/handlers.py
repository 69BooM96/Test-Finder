import json

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from Core import *


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("start")

@router.message(Command("help"))
async def help(message: Message): 
    await message.answer("help")

@router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)