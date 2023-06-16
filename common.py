from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
import Investing

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    Investing.create_table(message.from_user.id)
    await state.clear()
    await message.answer(
        text="Привет! Это демо-счёт с акциями мосбиржи. Введи свой депозит (в рублях):"
             "Если захочешь начать всё сначало, то просто напиши - /start",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Command(commands=["cancel"]))
@router.message(Text(text="отмена", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )