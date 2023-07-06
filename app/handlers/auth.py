from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from db.conn import session
from db.utils import get_user_by_login, update_user
from keyboards.keyboards import yes_no_kb
from keyboards.markup import set_employee_inline, set_director_inline
from states.states import Auth, Entered

router = Router(name="auth-router")


@router.message(Auth.logout)
async def echo_handler(message: Message, state: FSMContext) -> None:
    """
    Handler will forward received message back to the sender

    By default, message handler will handle all message types (like text, photo, sticker and etc.)
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


@router.message(Auth.set_login)
async def process_set_login(message: Message, state: FSMContext) -> None:
    """
    This handler set the user login
    """
    await state.update_data(login=message.text)
    await state.set_state(Auth.set_pass)
    await message.answer("Введите пароль")


async def number_of_attempts(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if 'attempt' not in data:
        await state.update_data(attempt=1)
        return
    if data['attempt'] >= 3:
        await state.clear()
        await state.set_state(Auth.logout)
        await message.answer("Превышен лимит попыток входа, пока")
    else:
        await state.update_data(attempt=data['attempt'] + 1)


@router.message(Auth.set_pass)
async def process_set_password(message: Message, state: FSMContext) -> None:
    """
    This handler set the user password
    """
    await number_of_attempts(message, state)
    password = message.text
    data = await state.get_data()
    user = get_user_by_login(session, data['login'])
    if not user:
        await state.set_state(Auth.set_login)
        await message.answer("Логин введен не верно, попробуйте еще раз")
        return
    if not user.check_password(password):
        await state.set_state(Auth.set_pass)
        await message.answer("Пароль введен не верно, попробуйте еще раз")
        return
    await state.clear()
    await state.set_state(Entered.change_tg_id)
    await state.update_data(user=user)
    await message.answer(
        f"Вы успешно вошли, {user.name} {user.surname}\nХотите привязать ваш аккаунт, что бы не пришлось вводить логин и пароль каждый раз?",
        reply_markup=yes_no_kb)


@router.message(Entered.change_tg_id, F.text.casefold() == "нет")
async def process_dont_change_tg_id(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(Entered.in_system)
    await message.answer(
        "Как хочешь 😅",
        reply_markup=ReplyKeyboardRemove(),
    )
    if data["user"].role == "employee":
        await message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
    else:
        await message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())


@router.message(Entered.change_tg_id, F.text.casefold() == "да")
async def process_change_tg_id(message: Message, state: FSMContext) -> None:
    await state.set_state(Entered.in_system)
    data = await state.get_data()

    if update_user(session, data['user'].id, **{"telegram_id": str(message.from_user.id)}):
        await message.reply(
            "<em>Уже поменял</em>",
            reply_markup=ReplyKeyboardRemove(),
        )

        if data["user"].role == "employee":
            await message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
        else:
            await message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())

    else:
        await message.reply("К сожалению я не смог его изменить",
                            reply_markup=ReplyKeyboardRemove())
        if data["user"].role == "employee":
            await message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
        else:
            await message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())


@router.message(Entered.change_tg_id)
async def process_unknown_change_tg_id(message: Message, state: FSMContext) -> None:
    await message.reply("Я тебя не понял :(")
