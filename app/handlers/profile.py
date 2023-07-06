from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.conn import session
from db.utils import update_user
from middlewares.middleware import CheckAuthMessageMiddleware
from states.states import Profile, Entered
from utils.utils import update_state_data_by_id, show_profile

router = Router(name="profile-router")
router.message.middleware(CheckAuthMessageMiddleware())


@router.message(Profile.change_name)
async def process_change_profile_name(message: Message, state: FSMContext):
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    user = update_user(session, data['user'].id, **{"name": message.text})
    if user:
        await update_state_data_by_id(data['user'].id, state)
        await show_profile(state, is_button=False, message=message)
    else:
        await message.answer("Не удалось сменить имя")
        await show_profile(state, is_button=False, message=message)


@router.message(Profile.change_surname)
async def process_change_profile_surname(message: Message, state: FSMContext):
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    user = update_user(session, data['user'].id, **{"surname": message.text})
    if user:
        await update_state_data_by_id(data['user'].id, state)
        await show_profile(state, is_button=False, message=message)
    else:
        await message.answer("Не удалось сменить фамилию")
        await show_profile(state, is_button=False, message=message)


@router.message(Profile.change_login)
async def process_change_profile_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    user = update_user(session, data['user'].id, **{"login": message.text})

    if user:
        await update_state_data_by_id(data['user'].id, state)
        await state.set_state(Entered.in_system)
        await message.answer("Логин успешно изменен")
        await show_profile(state, is_button=False, message=message)
    elif user is None:
        await message.answer("Даный логин уже занят, пожалуйста введите другой")
    else:
        await state.set_state(Entered.in_system)
        await message.answer("Не удалось сменить логин")
        await show_profile(state, is_button=False, message=message)


@router.message(Profile.old_password)
async def process_change_profile_password_old(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data["user"].check_password(message.text):
        await state.set_state(Entered.in_system)
        await message.answer("Пароль введен не правильно")
        await show_profile(state, is_button=False, message=message)
        return
    await state.set_state(Profile.change_password)
    await message.answer("Введите новый пароль")


@router.message(Profile.change_password)
async def process_change_profile_password(message: Message, state: FSMContext):
    await state.set_state(Profile.repeat_password)
    await state.update_data(password=f"{message.text}")
    await message.answer("Повторите пароль")


@router.message(Profile.repeat_password)
async def process_change_profile_password_repeat(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['password'] != message.text:
        await state.set_state(Profile.change_password)
        await message.answer("Пароли не совпадают, введите новый пароль еще раз")
        return

    data['user'].set_password(message.text)
    if update_user(session, data['user'].id, **{"password": data['user'].password}):
        await state.clear()
        await update_state_data_by_id(data['user'].id, state)
        await state.set_state(Entered.in_system)
        await message.answer("Пароль успешно изменен")
        await show_profile(state, is_button=False, message=message)
    else:
        await state.set_state(Entered.in_system)
        await message.answer("Не удалось сменить пароль")
        await show_profile(state, is_button=False, message=message)
