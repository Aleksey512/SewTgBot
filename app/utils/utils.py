from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.conn import session
from db.utils import get_user_by_id
from keyboards.markup import set_change_profile_inline

roles = {
    "employee": "Сотрудник",
    "director": "Директор",
    "admin": "Администратор"
}


async def update_state_data_by_id(user_id: int, state: FSMContext):
    user = get_user_by_id(session, user_id)
    await state.update_data(user=user)


async def show_profile(state: FSMContext, is_button: bool, query: CallbackQuery = None,
                       message: Message = None):
    data = await state.get_data()
    profile_info = f"Имя: <b>{data['user'].name}</b>\n" \
                   f"Фамилия: <b>{data['user'].surname}</b>\n" \
                   f"Роль: <b>{roles[data['user'].role]}</b>\n" \
                   f"TelegramID: <b>{data['user'].telegram_id}</b>\n" \
                   f"Дата создания: <b>{data['user'].created_at}</b>\n" \
                   f"Дата последнего обновления: <b>{data['user'].updated_at}</b>"
    if is_button:
        await query.message.answer(profile_info, reply_markup=set_change_profile_inline().as_markup())
    else:
        await message.answer(profile_info, reply_markup=set_change_profile_inline().as_markup())


def is_float(stroka: str):
    try:
        float(stroka)
        return True
    except ValueError:
        return False
