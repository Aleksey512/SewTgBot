import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import text

from db.conn import session
from db.utils import search_by_tg_id
from keyboards.markup import set_employee_inline, set_director_inline
from states.states import Auth, Entered

router = Router(name="commands-router")

START_MESSAGE = text(
    "<b>Я бот от 7versts</b> ✌️\n",
    "Пока что, мой функционал следующий:",
    "...functional...",
    "Однако в дальнейшем я стану большим и сильным 💪\n",
    "<b>Доступные команды</b> :",
    "<b>/start</b> - <em>Приветственное сообщение ✌️</em>",
    "<b>/login</b> - <em>Вход, начало работы 💸</em>",
    "<b>/menu</b> - <em>Меню пользователя</em>",
    "<b>/logout</b> - <em>Выйти из системы ❌</em>",
    sep="\n",
)


@router.message(Command("start"))
@router.message(F.text.casefold() == "start")
async def send_welcome(message: Message):
    """
    `/start` command
    """
    await message.answer(text=START_MESSAGE, parse_mode="HTML")


@router.message(Command(commands=["login"]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receive messages with `/login` command
    """
    await state.set_state(Auth.log_in)
    await message.answer("Привет, сейчас я проверю, есть ли вы в системе")
    user_id = message.from_user.id
    if user := search_by_tg_id(session, str(user_id)):
        await state.set_state(Entered.in_system)
        await state.update_data(user=user)
        await message.answer(f"Я вас нашел, {user.name} {user.surname}")

        if user.role == "employee":
            await message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
        else:
            await message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())
    else:
        await state.set_state(Auth.set_login)
        await message.answer(
            "К сожалению я вас не нашел, но вы можете попробовать войти по логину и паролю")
        await message.answer("Введите свой логин")


@router.message(Command("logout"))
@router.message(F.text.casefold() == "logout")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.reply("Вы и так были не в системе, но я на всякий случай вышел",
                            reply_markup=ReplyKeyboardRemove())
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Вы вышли",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("menu"))
@router.message(F.text.casefold() == "menu")
async def call_to_menu_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    if not "user" in data:
        await message.reply("Вы не вошли в систему")
        return

    if data["user"].role == "employee":
        await state.set_state(Entered.in_system)
        await message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
    else:
        await state.set_state(Entered.in_system)
        await message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())
