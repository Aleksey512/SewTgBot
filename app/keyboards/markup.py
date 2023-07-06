from aiogram.utils.keyboard import InlineKeyboardBuilder


def set_employee_inline() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Профиль", callback_data="menu_get_profile")
    kb.button(text="Управление", callback_data="menu_work_employee")
    kb.button(text="Статистика", callback_data="menu_get_statistics_employee")

    kb.adjust(1)
    return kb


def set_menu_get_statistics_employee_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Общая статистика", callback_data="employee_all_statistics")
    kb.button(text="Детальная статистика", callback_data="employee_detail_statistics")
    kb.button(text="<< Назад", callback_data="cp_back")

    kb.adjust(1)
    return kb


def return_to_main() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="Прервать операцию", callback_data="cp_back")
    kb.adjust(1)
    return kb


def ewm_procedures(procedures) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for proc in procedures:
        kb.button(text=f"{proc.name}",
                  callback_data=f"ewm_proc_{proc.id}")
    kb.button(text="<< Назад", callback_data="cp_back")
    kb.adjust(1)
    return kb


def set_change_profile_inline() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Поменять имя", callback_data="cp_name")
    kb.button(text="Поменять фамилию", callback_data="cp_surname")
    kb.button(text="Поменять логин", callback_data="cp_login")
    kb.button(text="Поменять пароль", callback_data="cp_password")
    kb.button(text="<< Назад", callback_data="cp_back")

    kb.adjust(2)
    return kb


def set_director_inline() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Профиль", callback_data="menu_get_profile")
    kb.button(text="Управление", callback_data="menu_manage_employee")
    kb.button(text="Статистика", callback_data="menu_get_statistic_director")

    kb.adjust(1)
    return kb


def set_director_main_inline() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Меню сотрудников", callback_data="dme_employee")
    kb.button(text="Меню бригад", callback_data="dme_brigade")
    kb.button(text="Меню объектов", callback_data="dme_objects")
    kb.button(text="<< Назад", callback_data="cp_back")

    kb.adjust(1)
    return kb


def set_director_employee_menu() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Список сотрудников", callback_data="dem_list")
    kb.button(text="Добавить сотрудника", callback_data="dem_create")
    kb.button(text="Назначить сотрудника в бригаду", callback_data="dem_to_brigade")
    kb.button(text="Удалить сотрудников", callback_data="dem_delete")
    kb.button(text="<< Назад", callback_data="back_to_main")
    kb.adjust(1)

    return kb


def set_director_brigade_menu() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Список бригад", callback_data="dbm_list")
    kb.button(text="Создать бригаду", callback_data="dbm_create")
    kb.button(text="Назначить бригаде объект", callback_data="dbm_object")
    kb.button(text="Удалить бригаду", callback_data="dbm_delete")
    kb.button(text="<< Назад", callback_data="back_to_main")

    kb.adjust(1)

    return kb


def set_director_object_menu() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text="Объекты", callback_data="dom_menu")
    kb.button(text="Процедуры ", callback_data="dpm_menu")
    kb.button(text="<< Назад", callback_data="back_to_main")

    kb.adjust(1)

    return kb


def set_director_object_menu_object() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="Список объектов", callback_data="dom_list")
    kb.button(text="Создать объект", callback_data="dom_create")
    kb.button(text="Удалить объект", callback_data="dom_delete")
    kb.button(text="<< Назад", callback_data="back_to_main_object_menu")

    kb.adjust(1)
    return kb


def set_director_object_menu_procedure() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="Список процедур у объекта", callback_data="dpm_list")
    kb.button(text="Создать продецуры у объекта", callback_data="dpm_create")
    kb.button(text="Удалить продецуры у объекта", callback_data="dpm_delete")
    kb.button(text="<< Назад", callback_data="back_to_main_object_menu")

    kb.adjust(1)
    return kb


def sbte_emloyee_kb(employee) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for user, _ in employee:
        kb.button(text=f"№ {user.id}: {user.name} {user.surname}", callback_data=f"sbte_emp_{user.id}")
    kb.button(text="<< Назад", callback_data="back_to_employee_menu")
    kb.adjust(2 if len(employee) <= 10 else 3)

    return kb


def sbte_brigade_kb(brigades) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for brigade in brigades:
        kb.button(text=f"№ {brigade[0].number} {brigade[0].name if brigade[0].name else ''}",
                  callback_data=f"sbte_brg_{brigade[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_employee_menu")
    kb.adjust(2 if len(brigades) <= 10 else 3)
    return kb


def del_brigade_kb(brigades) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for brigade in brigades:
        kb.button(text=f"№ {brigade[0].number} {brigade[0].name if brigade[0].name else ''}",
                  callback_data=f"del_br_{brigade[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_brigade_menu")
    kb.adjust(2 if len(brigades) <= 10 else 3)
    return kb


def add_object_to_brigade_kb(brigades) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for brigade in brigades:
        kb.button(text=f"№ {brigade[0].number} {brigade[0].name if brigade[0].name else ''}",
                  callback_data=f"list_br_to_obj_{brigade[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_brigade_menu")
    kb.adjust(2 if len(brigades) <= 10 else 3)
    return kb


def add_object_to_brigade_2_kb(object_) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for obj in object_:
        kb.button(text=f"№ {obj[0].id} {obj[0].name if obj[0].name else ''}",
                  callback_data=f"list_obj_br_{obj[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_brigade_menu")
    kb.adjust(2 if len(object_) <= 10 else 3)
    return kb


def del_object_kb(object_) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for obj in object_:
        kb.button(text=f"№ {obj[0].id} {obj[0].name if obj[0].name else ''}",
                  callback_data=f"del_obj_{obj[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_object_menu")
    kb.adjust(2 if len(object_) <= 10 else 3)
    return kb


def list_object_procedures_kb(object_) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for obj in object_:
        kb.button(text=f"№ {obj[0].id} {obj[0].name if obj[0].name else ''}",
                  callback_data=f"list_obj_procedures_{obj[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_procedures_menu")
    kb.adjust(2 if len(object_) <= 10 else 3)
    return kb


def list_object_create_procedure_kb(object_) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for obj in object_:
        kb.button(text=f"№ {obj[0].id} {obj[0].name if obj[0].name else ''}",
                  callback_data=f"dpm_create_{obj[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_procedures_menu")
    kb.adjust(2 if len(object_) <= 10 else 3)
    return kb


def list_object_delete_procedure_kb(object_) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    for obj in object_:
        kb.button(text=f"№ {obj[0].id} {obj[0].name if obj[0].name else ''}",
                  callback_data=f"dpm_delete_{obj[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_procedures_menu")
    kb.adjust(2 if len(object_) <= 10 else 3)
    return kb


def procedures_delete_kb(procedures) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for proc in procedures:
        kb.button(text=f"{proc[0].name} ({proc[0].time}, {proc[0].tariff})",
                  callback_data=f"proc_delete_{proc[0].id}")
    kb.button(text="<< Назад", callback_data="back_to_procedures_menu")
    kb.adjust(1)
    return kb
