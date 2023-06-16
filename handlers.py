from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram.fsm.context import FSMContext
import Investing
from aiogram.filters.text import Text
from aiogram import Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

class Noname(StatesGroup):
   s = State()
   b = State()
   d = State()


#депозит
@router.message(Command('Dep'))
async def send_insert(message: types.Message, state: FSMContext):
   await message.reply("Введи цифрами свой депозит:")
   await state.set_state(Noname.d)

@router.message(Noname.d)
async def a(message: types.Message, state: FSMContext):
   await state.update_data(deposit = message.text)
   try:
      dep = await state.get_data()
      dep = float(dep['deposit'])
      if Investing.insert_main(message.from_user.id, dep) == True:
         await message.answer(f"Спасибо! Я записал твой депозит равный сумме {dep} р.")
      else:
         await message.answer(f"Ошибка. Попробуй ещё раз!")
      kb = [
        [types.KeyboardButton(text="Купить акцию")],
        [types.KeyboardButton(text="Продать акцию")],
        [types.KeyboardButton(text="Мой портфель")]
      ]
      keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
      await message.answer("Что хочешь сделать дальше?", reply_markup=keyboard)
   except ValueError:
      await message.answer("Некорректное значение депозита. Пожалуйста, введи число")
   await state.clear()

# цена акции
async def send_result(data):
   print(data)
   try:
      share_price = Investing.share_price(data)
      return share_price
   except Exception as e:
      return False


# покупка акций
@router.message(Text("Купить акцию"))
async def send_insert(message: types.Message, state: FSMContext):
   builder = InlineKeyboardBuilder()
   builder.row(types.InlineKeyboardButton(
         text="Тикеры акций и их стоимость", url="https://smart-lab.ru/q/shaRES/")
   )
   await message.reply("Напишите тикер акции, которую хочешь купить", reply_markup=builder.as_markup())
   await state.set_state(Noname.b)


@router.message(Noname.b)
async def a(message: types.Message, state: FSMContext):
   await state.update_data(ticker = message.text)
   ticker = await state.get_data()
   share_price = await send_result(ticker['ticker'])
   print(share_price, ticker)
   if share_price != False:
      Investing.insert_data(message.from_user.id,
                              message.text.upper(), share_price)
      Investing.change_deposit(message.from_user.id, -abs(share_price))
      await message.answer(f"Акция {message.text.upper()} добавлена в твой портфель!")
   else:
      await message.answer(f"Акция с таким тикером не существует или не торгуется на МОСБИРЖЕ!")

   await state.clear()


# продажа акций
@router.message(Text("Продать акцию"))
async def send_insert(message: types.Message, state: FSMContext):
   await message.reply("Напиши тикер акции, которую хочешь продать")
   await state.set_state(Noname.s)

@router.message(Noname.s)
async def a(message: types.Message, state: FSMContext):
   await state.update_data(ticker = message.text)
   ticker = await state.get_data()
   share_price = await send_result(ticker['ticker'])
   if share_price:
      Investing.update_data(message.from_user.id,
                              message.text.upper(), share_price, 1)
      Investing.change_deposit(message.from_user.id, share_price)
      await message.answer(f"Акция {message.text.upper()} продана!")
   else:
      await message.answer(f"Акции с таким тикером нет в твоем портфеле")

      await state.clear()


@router.message(Text("Мой портфель"))
async def info(message: types.Message):
   await message.answer("*" + "Твой депозит: " + str(Investing.info_deposit()).replace('.', '\\.') + "р" + "*", parse_mode="MarkdownV2")

   portfolio_info = Investing.info_stock(message.from_user.id)
   await message.answer(f'<b> {portfolio_info} </b>', parse_mode="HTML")