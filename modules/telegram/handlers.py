from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

import keyboards as kb

router = Router()
a = {}

@router.message(CommandStart())
async def start(message: Message):
    send = await message.answer("start", reply_markup=await kb.start())


@router.message(Command("help"))
async def help(message: Message): 
    await message.answer("help")

@router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
    a[str(message.from_user.id)] = {"test": []}
    a[str(message.from_user.id)]["test"].append(message.text)
    print(a)