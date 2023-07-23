import datetime
import io
import logging
import os
import re
from datetime import date
from decimal import Decimal
from pprint import pprint

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputFile, FSInputFile, BufferedInputFile

from db.conn import session
from db.utils import *
from keyboards.keyboards import yes_no_kb
from keyboards.markup import *
from states.states import Profile, Director, Entered, Employee
from utils.excel.to_excel import statistics_to_excel_cur_month
from utils.utils import show_profile

from calendar import monthrange
from openpyxl.writer.excel import save_virtual_workbook

router = Router(name="callbacks-router")


def create_folder_if_not_exists(folder_path) -> bool | None:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return True
    else:
        return


"""
Ниже идут все  CallbackQuery для профиля пользователя до строки 80
"""


@router.callback_query(Text('menu_get_profile'))
async def profile_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await show_profile(state, is_button=True, query=query)


@router.callback_query(Text('cp_name'))
async def change_profile_name_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Profile.change_name)
    await query.message.answer("Введите новое имя")


@router.callback_query(Text('cp_surname'))
async def change_profile_surname_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Profile.change_surname)
    await query.message.answer("Введите новую фамилию")


@router.callback_query(Text('cp_login'))
async def change_profile_login_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Profile.change_login)
    await query.message.answer("Введите новый логин")


@router.callback_query(Text('cp_password'))
async def change_profile_password_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Profile.old_password)
    await query.message.answer("Введите старый пароль")


@router.callback_query(Text('cp_back'))
async def change_profile_return_button(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()

    if data["user"].role == "employee":
        await query.message.answer("Выберите действие: ", reply_markup=set_employee_inline().as_markup())
    else:
        await query.message.answer("Выберите действие: ", reply_markup=set_director_inline().as_markup())


"""
Ниже идут все  CallbackQuery для директора до строки 515
"""


@router.callback_query(Text('menu_manage_employee'))
async def menu_manage_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("Меню управления\n\n<b>Выберите действие:</b>",
                               reply_markup=set_director_main_inline().as_markup(), parse_mode="HTML")


@router.callback_query(Text('dme_employee'))
async def director_manage_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Меню сотрудников</em>\n\n<b>Выберите действие:</b>",
                               reply_markup=set_director_employee_menu().as_markup(), parse_mode="HTML")


@router.callback_query(Text('dme_brigade'))
async def director_manage_brigade(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Меню бригад</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_brigade_menu().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('dme_objects'))
async def director_manage_brigade(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Меню объектов и продедур</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('dem_list'))
async def dem_list(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_employee(session)
    if len(data) == 0:
        await query.message.answer(f"Сотрудников нет", reply_markup=set_director_employee_menu().as_markup())
        return
    text = ''
    for user, brigade in data:
        text += f"Сотрудник №: <b>{user.id}</b>\n" \
                f"Имя: <b>{user.name}</b>\n" \
                f"Фамилия: <b>{user.surname}</b>\n" \
                f"№ бригады: <b>{brigade.number if brigade else 'Неизвестно'}</b>\n\n"
    await query.message.answer(text, parse_mode="HTML", reply_markup=set_director_employee_menu().as_markup())


@router.callback_query(Text("dem_create"))
async def dem_create(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.ce_name)
    await query.message.answer("Введите имя сотрудника")


@router.callback_query(Text("dem_delete"))
async def dem_delete(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.delete_employee_first)
    await query.message.answer("Введите номер сотрудника, или номера сотрудников через запятую")


@router.callback_query(Text('dem_to_brigade'))
async def dem_to_brigade(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_employee(session)
    if len(data) == 0:
        await state.set_state(Entered.in_system)
        await query.message.answer(
            f"Сотрудников нет\n\n<em>Добавьте сотрудников для дальнейшей работы</em>",
            reply_markup=set_director_employee_menu().as_markup())
        return
    await query.message.answer("<em>Выберите сотрудника: </em>\n",
                               reply_markup=sbte_emloyee_kb(data).as_markup())


@router.callback_query(Text(startswith="sbte_emp_"))
async def dem_to_brigade_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.update_data(sbte_user_id=int(re.search(r"\d+", query.data).group(0)))
    data = get_all_brigades(session)
    if len(data) == 0:
        await state.set_state(Entered.in_system)
        await query.message.answer(
            f"Бригад нет\n\n<em>Добавьте бригаду, для дальнейшей работы</em>",
            reply_markup=set_director_employee_menu().as_markup())
        return
    await query.message.answer("Выберите бригаду в которую хотите добавить сотрудника",
                               reply_markup=sbte_brigade_kb(data).as_markup())


@router.callback_query(Text(startswith="sbte_brg_"))
async def dem_to_brigade_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()

    result = update_user(session, data['sbte_user_id'], **{"brigade_id": int(re.search(r"\d+", query.data).group(0))})
    if result:
        await state.set_state(Entered.in_system)
        await state.clear()
        await state.update_data(user=data["user"])
        await query.message.answer(f"<em>Сотрудник № <b>{data['sbte_user_id']}</b> успешно добавилен в бригаду</em>",
                                   reply_markup=set_director_employee_menu().as_markup())
    else:
        await state.set_state(Entered.in_system)
        await state.clear()
        await state.update_data(user=data["user"])
        await query.message.answer(f"<em>Возникла ошибка при добавлении сотрудника в бригаду</em>",
                                   reply_markup=set_director_employee_menu().as_markup())


@router.callback_query(Text('dbm_list'))
async def dbm_list(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_brigades(session)
    if len(data) == 0:
        await query.message.answer(f"Бригад нет", reply_markup=set_director_brigade_menu().as_markup())
        return
    text = ''
    for brigade in data:
        text += f"№ бригады: <b>{brigade[0].number}</b>\n" \
                f"Название бригады: <b>{brigade[0].name}</b>\n" \
                f"Количество сотрудников в бригаде: <b>{len(brigade[0].user)}</b>\n" \
                f"{'Назначенный объект бригаде: <b>' + str(brigade[0].objects.name) + '</b>' if brigade[0].objects else '<b>Бригаде не назначен объект</b>'}\n\n"
        print(brigade[0].objects)
    await query.message.answer(text, parse_mode="HTML", reply_markup=set_director_brigade_menu().as_markup())


@router.callback_query(Text("dbm_create"))
async def dbm_create(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.cb_number)
    await query.message.answer("Введите номер бригады")


@router.callback_query(Text("dbm_delete"))
async def dbm_delete(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_brigades(session)
    if len(data) == 0:
        await query.message.answer(f"Бригад нет", reply_markup=set_director_brigade_menu().as_markup())
        return

    await query.message.answer("Выберте бригаду которую хотите удалить", reply_markup=del_brigade_kb(data).as_markup())


@router.callback_query(Text("dbm_object"))
async def dbm_object(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_brigades(session)
    if len(data) == 0:
        await query.message.answer(f"Бригад нет", reply_markup=set_director_brigade_menu().as_markup())
        return

    await query.message.answer("Выберте бригаду которой хотите назначнить объект",
                               reply_markup=add_object_to_brigade_kb(data).as_markup())


@router.callback_query(Text(startswith="list_br_to_obj_"))
async def list_br_to_obj(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"<em>Объектов нет</em>", reply_markup=set_director_brigade_menu().as_markup())
        return
    await state.update_data(br_id=int(re.search(r"\d+", query.data).group(0)))
    await query.message.answer("Выберите назначаемый объект", reply_markup=add_object_to_brigade_2_kb(data).as_markup())


@router.callback_query(Text(startswith="list_obj_br_"))
async def list_obj_br_(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    try:
        brigade = get_brigade_by_id(session, data['br_id'])
        obj = get_object_by_id(session, int(re.search(r"\d+", query.data).group(0)))
        brigade.objects = obj
        session.add(brigade)
        session.commit()
        await query.message.answer(f"Объект {obj.name} назначен бригаде №{brigade.number}",
                                   reply_markup=set_director_brigade_menu().as_markup())
    except Exception as e:
        session.rollback()
        logging.error(f"UpdateBrigadeException {e}")
        await query.message.answer("Не удалось назначить объект бригаде",
                                   reply_markup=set_director_brigade_menu().as_markup())


@router.callback_query(Text(startswith="del_br_"))
async def dbm_delete_del_br(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.del_brigade_confirm)
    await state.update_data(del_br_id=int(re.search(r"\d+", query.data).group(0)))

    await query.message.answer("Вы действительно хотите удалить бригаду?", reply_markup=yes_no_kb)


@router.callback_query(Text('dom_menu'))
async def director_object_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Объекты</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu_object().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text("dom_list"))
async def director_objects_list(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"<em>Объектов нет</em>", reply_markup=set_director_object_menu_object().as_markup())
        return
    text = ''
    for obj in data:
        text += f"№ объекта: <b>{obj[0].id}</b>\n" \
                f"Название объекта: <b>{obj[0].name}</b>\n" \
                f"Количество процедур у объекта: <b>{len(obj[0].procedures)}</b>\n"
        if len(obj[0].brigades) != 0:
            text += "Бригады которые работают над объектом: "
            for br in obj[0].brigades:
                text += f"№{br.number} "
        text += "\n\n"
    await query.message.answer(text, reply_markup=set_director_object_menu_object().as_markup())


@router.callback_query(Text('dom_create'))
async def director_objects_create(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.create_object)
    await query.message.answer("Введите наименование объекта")


@router.callback_query(Text("dom_delete"))
async def director_objects_delete(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"Объетов нет", reply_markup=set_director_object_menu().as_markup())
        return

    await query.message.answer("Выберте объект который хотите удалить", reply_markup=del_object_kb(data).as_markup())


@router.callback_query(Text(startswith="del_obj_"))
async def director_del_obj(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.del_obj_confirm)
    obj = get_object_by_id(session, int(re.search(r"\d+", query.data).group(0)))
    await state.update_data(obj=obj)

    await query.message.answer(f"Вы действительно хотите удалить {obj.name}?", reply_markup=yes_no_kb)


@router.callback_query(Text('dpm_menu'))
async def director_procedure_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Процедуры</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu_procedure().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('dpm_list'))
async def director_procedure_list(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"<em>Объектов нет</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())
        return
    await query.message.answer("Выберте объект у которого хотите посмотреть процедуры",
                               reply_markup=list_object_procedures_kb(data).as_markup())


@router.callback_query(Text(startswith="list_obj_procedures_"))
async def director_procedures_list_next(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_procedures_by_object_id(session, int(re.search(r"\d+", query.data).group(0)))
    if len(data) == 0:
        await query.message.answer(f"<em>У данного объекта нет процедур</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())
        return
    text_ = ''
    time = 0
    rate = 0
    for procedure in data:
        text_ += f"Название: <b>{procedure[0].name}</b>\n" \
                 f"Время: <b>{procedure[0].time}</b>\n" \
                 f"Тариф: <b>{round(procedure[0].tariff, 1)}</b>\n" \
                 f"Расценка: <b>{round(procedure[0].rate, 1)}</b>\n\n"
        time += procedure[0].time
        rate += procedure[0].rate
    text_ += f"Итого затрачено времени на объект: <b>{time}</b> ед.\n" \
             f"Итого расценка за объект: <b>{round(rate, 1)}</b> руб."
    await query.message.answer(text_, reply_markup=set_director_object_menu_procedure().as_markup())


@router.callback_query(Text('dpm_create'))
async def director_create_object_procedures(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"<em>Объектов нет</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())
        return
    await query.message.answer("Выберте объект для которого хотите добавить процедуру",
                               reply_markup=list_object_create_procedure_kb(data).as_markup())


@router.callback_query(Text(startswith="dpm_create_"))
async def director_list_obj_to_create_procedures(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Director.create_procedure_name)
    await state.update_data(obj_id=int(re.search(r"\d+", query.data).group(0)))
    await query.message.answer("Введите название процедуры")


@router.callback_query(Text("dpm_delete"))
async def director_delete_procedure(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = get_all_objects(session)
    if len(data) == 0:
        await query.message.answer(f"<em>Объектов нет</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())
        return
    await query.message.answer("Выберте объект у которого хотите удалить процедуру",
                               reply_markup=list_object_delete_procedure_kb(data).as_markup())


@router.callback_query(Text(startswith="dpm_delete_"))
async def dpm_delete_(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    obj_id = int(re.search(r"\d+", query.data).group(0))
    await state.update_data(obj_id=obj_id)
    data = get_procedures_by_object_id(session, obj_id)
    if len(data) == 0:
        await query.message.answer(f"<em>У бъекта нет процедур</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())
        return
    await query.message.answer("Выберите процедуру которую хотите удалить\n<em>Название (время, тариф)</em>",
                               reply_markup=procedures_delete_kb(data).as_markup())


@router.callback_query(Text(startswith="proc_delete_"))
async def proc_delete_(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    proc_id = int(re.search(r"\d+", query.data).group(0))
    if delete_procedure_by_id(session, proc_id):
        data_proc = get_procedures_by_object_id(session, data['obj_id'])
        if len(data_proc) == 0:
            await query.message.answer(f"<em>У объекта больше нет процедур</em>",
                                       reply_markup=set_director_object_menu_procedure().as_markup())
            return
        await query.message.answer(
            "<em>Успешно</em>\n\nВыберите процедуру которую хотите удалить\n<em>Название (время, тариф)</em>",
            reply_markup=procedures_delete_kb(data_proc).as_markup())
    else:
        await state.clear()
        await state.update_data(user=data['user'])
        await query.message.answer("<em>Не удалось удалить процедуру</em>",
                                   reply_markup=set_director_object_menu_procedure().as_markup())


@router.callback_query(Text('back_to_main'))
async def back_to_main(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Меню управления</em>\n<em>Выберите действие:</em>",
                               reply_markup=set_director_main_inline().as_markup(), parse_mode="HTML")


@router.callback_query(Text('back_to_employee_menu'))
async def back_to_employee_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Меню сотрудников</em>\n<em>Выберите действие:</em>",
                               reply_markup=set_director_employee_menu().as_markup(), parse_mode="HTML")


@router.callback_query(Text('back_to_brigade_menu'))
async def back_to_brigade_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Меню бригад</em>\n<b>Выберите действие</b>:",
                               reply_markup=set_director_brigade_menu().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('back_to_main_object_menu'))
async def back_to_main_object_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Меню объектов и продедур</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('back_to_object_menu'))
async def back_to_object_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Объекты</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu_object().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('back_to_procedures_menu'))
async def back_to_procedure_menu(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)
    data = await state.get_data()
    await state.clear()
    await state.update_data(user=data['user'])
    await query.message.answer("<em>Процедуры</em>\n\n<b>Выберите действие</b>:",
                               reply_markup=set_director_object_menu_procedure().as_markup(),
                               parse_mode="HTML")


@router.callback_query(Text('menu_get_statistic_director'))
async def menu_get_statistic_director(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Entered.in_system)

    cur_data = datetime.now()
    month_max = monthrange(cur_data.year, cur_data.month)[1]
    data = get_all_information(session)
    wb = statistics_to_excel_cur_month(data, cur_data, month_max)
    f = save_virtual_workbook(wb)
    await query.message.answer_document(
        BufferedInputFile(f,
                          filename=f"Статистика c " +
                                   f"1.{cur_data.month}.{cur_data.year} по " +
                                   f"{month_max}.{cur_data.month}.{cur_data.year}.xlsx"),
        reply_markup=set_director_inline().as_markup()
    )


"""
Ниже идут все  CallbackQuery для сотрудника
"""


@router.callback_query(Text("menu_work_employee"))
async def menu_work_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    if data['user'].brigade_id is None:
        await query.message.answer("<em>Вы не состоите ни в одной бригаде</em>",
                                   reply_markup=set_employee_inline().as_markup())
        return
    brigade = get_brigade_by_id(session, data['user'].brigade_id)
    if brigade.objects is None:
        await query.message.answer("<em>Вашей бригаде не назначен объект</em>",
                                   reply_markup=set_employee_inline().as_markup())
        return
    procedures = brigade.objects.procedures
    if len(procedures) == 0:
        await query.message.answer("<em>У объекта над которым вы работаете нет процедур</em>",
                                   reply_markup=set_employee_inline().as_markup())
        return
    await query.message.answer("Выберите процедуру:", reply_markup=ewm_procedures(procedures).as_markup())


@router.callback_query(Text(startswith="ewm_proc_"))
async def employee_set_proc(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(Employee.add_procedure)
    proc_id = int(re.search(r"\d+", query.data).group(0))
    await state.update_data(proc_id=proc_id)
    await query.message.answer("<em>Введите количество</em>", reply_markup=return_to_main().as_markup())


@router.callback_query(Text("menu_get_statistics_employee"))
async def menu_get_statistics_employee(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("<em>Статистика</em>", reply_markup=set_menu_get_statistics_employee_kb().as_markup())


@router.callback_query(Text("employee_all_statistics"))
async def employee_all_statistics(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    cur_proc = get_cur_month_procedure(session, data['user'].id)
    if len(cur_proc) == 0:
        await query.message.answer(f"<em>За этот месяц не было произведено ни одной операции</em>",
                                   reply_markup=set_menu_get_statistics_employee_kb().as_markup())
        return
    money_month = 0
    money_day = 0
    for proc, count, created_at, _ in cur_proc:
        if proc.rate == 0 or count == 0:
            continue
        if created_at == date.today():
            money_day += Decimal(count) * proc.rate
        money_month += Decimal(count) * proc.rate
    await query.message.answer(f"Заработано за текущий день: <b>{round(money_day, 1)} руб.</b>\n"
                               f"Заработано за текущий месяц: <b>{round(money_month, 1)} руб.</b>",
                               reply_markup=set_menu_get_statistics_employee_kb().as_markup())


@router.callback_query(Text("employee_detail_statistics"))
async def employee_detail_statistics(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    cur_proc = get_cur_month_procedure(session, data['user'].id)
    if len(cur_proc) == 0:
        await query.message.answer(f"<em>За этот месяц не было произведено ни одной операции</em>",
                                   reply_markup=set_menu_get_statistics_employee_kb().as_markup())
        return
    data = {}
    for proc, count, created_at, _ in cur_proc:
        if proc.rate == 0 or count == 0:
            continue
        if f'{created_at}' not in data:
            data[f'{created_at}'] = {proc.name: {proc.id: {'count': count,
                                                           'time': count * proc.time,
                                                           'money': Decimal(count) * proc.rate}}}
            continue
        if proc.name not in data[f'{created_at}']:
            data[f'{created_at}'][proc.name] = {proc.id: {'count': count,
                                                          'time': count * proc.time,
                                                          'money': Decimal(count) * proc.rate}}
            continue
        if proc.id not in data[f'{created_at}'][proc.name]:
            data[f'{created_at}'][proc.name][proc.id] = {'count': count,
                                                         'time': count * proc.time,
                                                         'money': Decimal(count) * proc.rate}
            continue
        data[f'{created_at}'][proc.name][proc.id]['count'] += count
        data[f'{created_at}'][proc.name][proc.id]['time'] += count * proc.time
        data[f'{created_at}'][proc.name][proc.id]['money'] += Decimal(count) * proc.rate
    pprint(data)
    text = ''
    all_count = 0
    all_money = 0
    all_time = 0
    for keys in data:
        text += f'<u><b>{keys}</b></u>\n\n'
        count = 0
        money = 0
        time = 0
        for name in data[keys]:
            text += f'<b>{name}</b>\n\n'
            for ids in data[keys][name]:
                text += f'<em><u>№ {ids}</u>\n' \
                        f'Количество: {data[keys][name][ids]["count"]}\n' \
                        f'Потраченное время: {data[keys][name][ids]["time"]}\n' \
                        f'Заработано: {round(data[keys][name][ids]["money"], 1)} руб.\n</em>'
                count += data[keys][name][ids]["count"]
                money += data[keys][name][ids]["money"]
                time += data[keys][name][ids]["time"]
            text += '\n'
        text += f'<b>Количество операций за этот день: {count}\n' \
                f'Потрачено времени за этот день {time}\n' \
                f'Заработано за это день: {round(money, 1)} руб.\n\n\n</b>'
        all_time += time
        all_money += money
        all_count += count
    text += f'<b>Количество операций за этот месяц: {all_count}\n' \
            f'Потрачено времени за этот месяц {all_time}\n' \
            f'Заработано за это месяц: {round(all_money, 1)} руб.\n\n\n</b>'
    await query.message.answer(text,
                               reply_markup=set_menu_get_statistics_employee_kb().as_markup())
