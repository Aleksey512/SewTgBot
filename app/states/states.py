from aiogram.fsm.state import State, StatesGroup


class Auth(StatesGroup):
    log_in = State()
    logout = State()
    set_login = State()
    set_pass = State()


class Entered(StatesGroup):
    change_tg_id = State()
    in_system = State()


class Profile(StatesGroup):
    change_name = State()
    change_surname = State()
    change_login = State()
    old_password = State()
    change_password = State()
    repeat_password = State()


class Director(StatesGroup):
    create_employee = State()
    ce_name = State()
    ce_surname = State()
    delete_employee_first = State()
    delete_employee_second = State()
    cb_number = State()
    cb_name = State()
    del_brigade_confirm = State()
    create_object = State()
    del_obj_confirm = State()
    create_procedure_name = State()
    create_procedure_time = State()
    create_procedure_tariff = State()
    confirm_create_procedure = State()


class Employee(StatesGroup):
    add_procedure = State()
