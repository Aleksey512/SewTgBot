from datetime import date

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.conn import session
from db.utils import add_user_procedure, get_cur_month_procedure
from keyboards.markup import return_to_main, set_employee_inline
from middlewares.middleware import CheckAuthMessageMiddleware
from states.states import Entered, Employee

from decimal import Decimal

router = Router(name="employee-router")
router.message.middleware(CheckAuthMessageMiddleware())


@router.message(Employee.add_procedure)
async def process_add_procedure(message: Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.answer("<em>Введите <b>число</b>, например <b>7</b></em>",
                             reply_markup=return_to_main().as_markup())
    if int(message.text) <= 0:
        await message.answer("Число должно быть больше нуля", reply_markup=return_to_main().as_markup())
    data = await state.get_data()
    if add_user_procedure(session, data['user'].id, data['proc_id'], int(message.text)):
        cur_proc = get_cur_month_procedure(session, data['user'].id)
        money_month = 0
        money_day = 0
        money_curr = 0
        for proc, count, created_at in cur_proc:
            if proc.rate == 0 or count == 0:
                continue
            if proc.id == data['proc_id']:
                money_curr += Decimal(count) * proc.rate
            if created_at == date.today():
                money_day += Decimal(count) * proc.rate
            money_month += Decimal(count) * proc.rate
        await state.set_state(Entered.in_system)
        await state.clear()
        await state.update_data(user=data['user'])
        await message.answer(f"<em>Успешно</em>\n\n"
                             f"Заработано за текущую операцию: <b>{money_curr}</b>\n"
                             f"Заработано за текущий день: <b>{money_day}</b>\n"
                             f"Заработано за текущий месяц: <b>{money_month}</b>",
                             reply_markup=set_employee_inline().as_markup())
    else:
        await state.set_state(Entered.in_system)
        await state.clear()
        await state.update_data(user=data['user'])
        await message.answer("<em>Неудачно, поробуйте ещё раз</em>",
                             reply_markup=set_employee_inline().as_markup())
