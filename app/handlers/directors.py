import re
import secrets
import string

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy import func

from db.conn import session
from db.models import User
from db.utils import (add_user,
                      delete_user_by_id,
                      get_all_users_by_ids,
                      search_brigade_by_number,
                      add_brigade,
                      delete_brigade_by_id,
                      add_object,
                      delete_object_by_id, add_procedure)
from keyboards.keyboards import yes_no_kb
from keyboards.markup import (set_director_employee_menu,
                              set_director_brigade_menu,
                              set_director_object_menu_object, set_director_object_menu_procedure)
from middlewares.middleware import CheckAuthMessageMiddleware
from states.states import Entered, Director
from utils.utils import is_float

router = Router(name="director-router")
router.message.middleware(CheckAuthMessageMiddleware())
alphabet = string.ascii_letters + string.digits


@router.message(Director.ce_name)
async def add_employee_name(message: Message, state: FSMContext):
    await state.update_data(ce_name=message.text)
    await state.set_state(Director.ce_surname)
    await message.answer("Введите фамилию")


@router.message(Director.ce_surname)
async def add_employee_surname(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Entered.in_system)
    await state.clear()
    await state.update_data(user=data['user'])
    last_id = session.query(func.max(User.id)).scalar()
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    new_user = add_user(session,
                        login=f"employee{last_id + 1}",
                        password=password,
                        name=data['ce_name'],
                        surname=message.text)
    if new_user:
        text = f"<em><b>Успешно</b></em>\n\n" \
               f"Сотрудник №: <b>{new_user.id}</b>\n" \
               f"Имя: <b>{new_user.name}</b>\n" \
               f"Фамилия: <b>{new_user.surname}</b>\n" \
               f"Login: <b>{new_user.login}</b>\n" \
               f"Password: <b>{password}</b>\n\n" \
               f"<em>Отправьте это сообщение сотруднику, он сможет войти по логину и паролю</em>"
        await message.answer(text, parse_mode="HTML", reply_markup=set_director_employee_menu().as_markup())
    else:
        await message.answer("Не удалось добавить сотрудника", reply_markup=set_director_employee_menu().as_markup())


@router.message(Director.delete_employee_first)
async def delete_employee(message: Message, state: FSMContext):
    ids = [int(i) for i in re.findall(r'\d+', message.text)]
    if len(ids) == 0:
        await message.answer("Вы не ввели ни одного числа", reply_markup=set_director_employee_menu().as_markup())
        return
    data = get_all_users_by_ids(session, ids)
    if len(data) != 0:
        text = "<em>Вы уверены, что хотите удалить следующих сотрудников?</em> \n\n"
        for user in data:
            text += f"Сотрудник №: <b>{user[0].id}</b>\n" \
                    f"Имя: <b>{user[0].name}</b>\n" \
                    f"Фамилия: <b>{user[0].surname}</b>\n\n"
        await state.update_data(ids=ids)
        await state.set_state(Director.delete_employee_second)
        await message.answer(text, parse_mode="HTML", reply_markup=yes_no_kb)
    else:
        await state.set_state(Entered.in_system)
        await message.answer("Таких сотрудников не существует", reply_markup=set_director_employee_menu().as_markup())


@router.message(Director.delete_employee_second, F.text.casefold() == "нет")
async def process_dont_delete_employee(message: Message, state: FSMContext) -> None:
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()
    await state.set_state(Entered.in_system)
    await message.answer("<em>Меню сотрудников</em>\n<b>Выберите действие:</b>",
                         reply_markup=set_director_employee_menu().as_markup(), parse_mode="HTML")


@router.message(Director.delete_employee_second, F.text.casefold() == "да")
async def process_delete_employee(message: Message, state: FSMContext) -> None:
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    result = delete_user_by_id(session, data["ids"])
    await state.clear()
    await state.update_data(user=data['user'])
    if result:
        await message.answer("<em>Сотрудники успешно удалены</em>\n", parse_mode="HTML",
                             reply_markup=set_director_employee_menu().as_markup())
    else:
        await message.answer("<em>Не удалось удалить сотрудников</em>\n", parse_mode="HTML",
                             reply_markup=set_director_employee_menu().as_markup())


@router.message(Director.delete_employee_second)
async def process_unknown_delete_employee(message: Message, state: FSMContext) -> None:
    await message.reply("Я тебя не понял :(")


@router.message(Director.cb_number)
async def create_brigade_number(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        await message.answer("Введите <b>число</b>, например <b>7</b> !")
        return
    if search_brigade_by_number(session, int(message.text)):
        await message.answer("Бригада с таким номером уже существует, введите другой номер")
        return
    await state.update_data(cb_number=int(message.text))
    await state.set_state(Director.cb_name)
    await message.answer("Введите название бригады")


@router.message(Director.cb_name)
async def create_brigade_name(message: Message, state: FSMContext):
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    new_brigade = add_brigade(session, data['cb_number'], message.text)
    await state.clear()
    await state.update_data(user=data['user'])
    if new_brigade:
        await message.answer(f"<em>Бригада № {new_brigade.number} успешно создана</em>",
                             reply_markup=set_director_brigade_menu().as_markup())
    else:
        await message.answer("Не удалось создать бригаду", reply_markup=set_director_brigade_menu().as_markup())


@router.message(Director.del_brigade_confirm, F.text.casefold() == "да")
async def process_delete_brigade(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()

    await state.set_state(Entered.in_system)
    data = await state.get_data()

    await state.clear()
    await state.update_data(user=data['user'])

    if delete_brigade_by_id(session, data["del_br_id"]):
        await message.answer("<em>Бригада успешно удалена</em>", reply_markup=set_director_brigade_menu().as_markup())
    else:
        await message.answer("<em>Не удалось удалить бригаду</em>",
                             reply_markup=set_director_brigade_menu().as_markup())


@router.message(Director.del_brigade_confirm, F.text.casefold() == "нет")
async def process_no_delete_brigade(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()
    await state.set_state(Entered.in_system)
    await message.answer("<em>Меню бригад</em>\n<b>Выберите действие</b>:",
                         reply_markup=set_director_brigade_menu().as_markup(),
                         parse_mode="HTML")


@router.message(Director.del_brigade_confirm)
async def process_unknown_delete_brigade(message: Message, state: FSMContext) -> None:
    await message.reply("Я тебя не понял :(")


@router.message(Director.create_object)
async def process_create_object(message: Message, state: FSMContext) -> None:
    await state.set_state(Entered.in_system)
    if obj := add_object(session, message.text):
        await message.answer(
            f"<b>Успешно добавлен</b>\n\n<em>Объект <b>№{obj.id}</b>\nНазвание: <b>{obj.name}</b></em>",
            reply_markup=set_director_object_menu_object().as_markup())
    else:
        await message.answer("Не удалось добавить объект",
                             reply_markup=set_director_object_menu_object().as_markup())


@router.message(Director.del_obj_confirm, F.text.casefold() == "да")
async def process_delete_object(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()

    await state.set_state(Entered.in_system)
    data = await state.get_data()

    await state.clear()
    await state.update_data(user=data['user'])

    if delete_object_by_id(session, data['obj'].id):
        await message.answer(
            f"Успешно удален\n\n<em>Объект <b>№{data['obj'].id}</b>\nНазвание: <b>{data['obj'].name}</b></em>",
            reply_markup=set_director_object_menu_object().as_markup())
    else:
        await message.answer("<em>Не удалось удалить объект</em>",
                             reply_markup=set_director_object_menu_object().as_markup())


@router.message(Director.del_obj_confirm, F.text.casefold() == "нет")
async def process_no_delete_object(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()
    await state.set_state(Entered.in_system)
    await message.answer("<em>Объекты</em>\n\n<b>Выберите действие</b>:",
                         reply_markup=set_director_object_menu_object().as_markup(),
                         parse_mode="HTML")


@router.message(Director.del_obj_confirm)
async def process_unknown_delete_object(message: Message, state: FSMContext) -> None:
    await message.reply("Я тебя не понял :(")


@router.message(Director.create_procedure_name)
async def process_procedure_name(message: Message, state: FSMContext):
    await state.set_state(Director.create_procedure_time)
    await state.update_data(p_name=message.text)
    await message.answer("Введите затрачиваемое время на процедуру")


@router.message(Director.create_procedure_time)
async def process_procedure_time(message: Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.answer("Введите <b>число</b>, например <b>7</b> !")
        return
    await state.set_state(Director.create_procedure_tariff)
    await state.update_data(p_time=message.text)
    await message.answer("Введите тариф для процедуры")


@router.message(Director.create_procedure_tariff)
async def process_procedure_tariff(message: Message, state: FSMContext):
    if not is_float(message.text):
        await message.answer("Введите <b>число</b>, например <b>7</b> или 0.7 (через точку)!")
        return
    data = await state.get_data()
    if add_procedure(session,
                     data['obj_id'],
                     data['p_name'],
                     data['p_time'],
                     float(message.text),
                     round(float(data['p_time']) * float(message.text), 2)):
        await state.set_state(Director.confirm_create_procedure)
        await message.answer("<em>Процедура успешно добавлена</em>")
        await message.answer("Хотите добавить еще одну процедуру?", reply_markup=yes_no_kb)
    else:
        await state.set_state(Entered.in_system)
        await state.clear()
        await state.update_data(user=data['user'])
        await message.answer("<em>Не удалось добавить процедуру</em>",
                             reply_markup=set_director_object_menu_procedure().as_markup())


@router.message(Director.confirm_create_procedure, F.text.casefold() == "да")
async def process_confirm_procedure(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()

    await state.set_state(Director.create_procedure_name)
    await message.answer("Введите название процедуры")


@router.message(Director.confirm_create_procedure, F.text.casefold() == "нет")
async def process_no_confirm_procedure(message: Message, state: FSMContext):
    ms = await message.answer(text="ok", reply_markup=ReplyKeyboardRemove())
    await ms.delete()
    data = await state.get_data()
    user = data['user']
    await state.set_state(Entered.in_system)
    await state.clear()
    await state.update_data(user=data['user'])
    await message.answer("<em>Процедуры</em>\n\n<b>Выберите действие</b>:",
                         reply_markup=set_director_object_menu_procedure().as_markup(),
                         parse_mode="HTML")


@router.message(Director.confirm_create_procedure)
async def process_unknown_confirm_procedure(message: Message, state: FSMContext) -> None:
    await message.reply("Я тебя не понял :(")
