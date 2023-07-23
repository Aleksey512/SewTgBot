import logging
from datetime import datetime
from typing import List, Any, Sequence

import sqlalchemy.exc
from dateutil.relativedelta import relativedelta
from sqlalchemy import select, update, and_, Row, func
from sqlalchemy.orm import Session, joinedload, contains_eager

from db.models import User, Brigade, Object, Procedure, User_Procedure


def get_user_by_id(session: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return session.execute(stmt).scalar()


def search_by_tg_id(session: Session, tg_id: str) -> User | None:
    stmt = select(User).where(User.telegram_id == tg_id)
    return session.execute(stmt).scalar()


def get_user_by_login(session, login: str) -> User | None:
    stmt = select(User).where(User.login == login)
    return session.execute(stmt).scalar()


def get_all_employee(session: Session) -> Sequence[Row[tuple[Any, ...] | Any]]:
    stmt = select(User, Brigade).filter(User.role == "employee").outerjoin(Brigade, Brigade.id == User.brigade_id)
    return session.execute(stmt).all()


def get_all_brigades(session: Session) -> Sequence[Row[tuple[Any, ...] | Any]]:
    stmt = select(Brigade)
    return session.execute(stmt).all()


def get_all_objects(sessions: Session):
    stmt = select(Object)
    return sessions.execute(stmt).all()


def get_all_procedures_by_object(session: Session, object_id: int):
    stmt = select(Procedure).filter(Procedure.object_id == object_id)
    return session.execute(stmt).all()


def get_all_information(session: Session):
    start_month = datetime(datetime.now().year, datetime.now().month, 1, 0, 0, 1)
    end_month = start_month + relativedelta(months=1)

    query = session.query(Brigade). \
        join(Brigade.user). \
        join(User.procedures). \
        options(contains_eager(Brigade.user).contains_eager(User.procedures))\
        .filter(and_(
            func.date(User_Procedure.created_at) >= start_month,
            func.date(User_Procedure.created_at) < end_month
        )).\
        all()

    return query


def search_brigade_by_number(session: Session, number: int) -> Brigade | None:
    stmt = select(Brigade).where(Brigade.number == number)
    return session.execute(stmt).scalar()


def get_brigade_by_id(session: Session, br_id: int) -> Brigade | None:
    stmt = select(Brigade).where(Brigade.id == br_id)
    return session.execute(stmt).scalar()


def get_object_by_id(session: Session, obj_id) -> Object | None:
    stmt = select(Object).filter_by(id=obj_id)
    return session.execute(stmt).scalar()


def get_procedures_by_object_id(session: Session, object_id: int):
    stmt = select(Procedure).where(Procedure.object_id == object_id)
    return session.execute(stmt).all()


def get_all_users_by_ids(session: Session, user_ids: List[int]) -> Sequence[Row[tuple[Any, ...] | Any]] | bool | None:
    try:
        stmt = select(User).filter(and_(User.id.in_(user_ids), User.role == "employee"))
        return session.execute(stmt).all()
    except sqlalchemy.exc.NoResultFound:
        session.rollback()
        logging.info("DeleteUserException - No result found error")
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"DeleteUserException {e}")
        return None


def get_cur_month_procedure(session: Session, user_id: int) -> Sequence[Row[tuple[Any, ...] | Any]]:
    start_month = datetime(datetime.now().year, datetime.now().month, 1, 0, 0, 1)
    end_month = start_month + relativedelta(months=1)
    stmt = select(Procedure, User_Procedure.count, User_Procedure.created_at, User_Procedure.id).join(
        User_Procedure).filter(
        and_(
            User_Procedure.user_id == user_id,
            func.date(User_Procedure.created_at) >= start_month,
            func.date(User_Procedure.created_at) < end_month
        )).order_by(User_Procedure.id.desc())
    return session.execute(stmt).all()


def delete_user_by_id(session: Session, user_ids: List[int]) -> bool | None:
    try:
        stmt = session.query(User).filter(and_(User.id.in_(user_ids), User.role == "employee")).all()
        for item in stmt:
            session.delete(item)
        session.commit()
        session.close()
        return True
    except sqlalchemy.exc.NoResultFound:
        session.rollback()
        logging.info("DeleteUserException - No result found error")
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"DeleteUserException {e}")
        return None


def delete_brigade_by_id(session: Session, brigade_id: int) -> bool | None:
    try:
        stmt = session.query(Brigade).filter(Brigade.id == brigade_id).scalar()
        session.delete(stmt)
        session.commit()
        session.close()
        return True
    except sqlalchemy.exc.NoResultFound:
        session.rollback()
        logging.info("DeleteBrigadeException - No result found error")
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"DeleteBrigadeException {e}")
        return None


def delete_object_by_id(session: Session, object_id: int) -> bool | None:
    try:
        stmt = session.query(Object).filter(Object.id == object_id).scalar()
        session.delete(stmt)
        session.commit()
        session.close()
        return True
    except sqlalchemy.exc.NoResultFound:
        session.rollback()
        logging.info("DeleteObjectException - No result found error")
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"DeleteObjectException {e}")
        return


def delete_procedure_by_id(session: Session, procedure_id: int) -> bool | None:
    try:
        stmt = session.query(Procedure).filter(Procedure.id == procedure_id).scalar()
        session.delete(stmt)
        session.commit()
        session.close()
        return True
    except sqlalchemy.exc.NoResultFound:
        session.rollback()
        logging.info("DeleteProcedureException - No result found error")
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"DeleteProcedureException {e}")
        return None


def add_user(session: Session,
             login: str,
             password: str,
             telegram_id: str = None,
             role: str = "employee",
             name: str = None,
             surname: str = None) -> User | None:
    try:
        new_user = User(name=name, surname=surname, telegram_id=telegram_id, login=login, role=role)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()
        session.close()
        return new_user
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        logging.warning(f"UserExistsException - User already exists")
        return None


def add_brigade(session: Session,
                number: int,
                name: str = None,
                ) -> Brigade | None:
    try:
        new_brigade = Brigade(name=name, number=number)
        session.add(new_brigade)
        session.commit()
        session.close()
        return new_brigade
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        logging.warning(f"BrigadeExistsException - Brigade already exists")
        return None


def add_object(session: Session,
               name: str,
               ) -> Object:
    new_object = Object(name=name)
    session.add(new_object)
    session.commit()
    session.close()
    return new_object


def add_procedure(session: Session,
                  object_id: int,
                  name: str,
                  time: int,
                  tariff: float,
                  rate: float,
                  ) -> Procedure | None:
    try:
        new_procedure = Procedure(object_id=object_id, name=name, time=time, tariff=tariff, rate=rate)
        session.add(new_procedure)
        session.commit()
        session.close()
        return new_procedure
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        logging.warning(f"ProcedureIntegrityError")
        return
    except Exception as e:
        session.rollback()
        logging.error(f"AddProcedureException {e}")
        return


def add_user_procedure(session: Session,
                       user_id: int,
                       procedure_id: int,
                       count: int) -> User_Procedure | bool:
    try:
        stmt = User_Procedure(user_id=user_id, procedure_id=procedure_id, count=count)
        session.add(stmt)
        session.commit()
        session.close()
        return stmt
    except Exception as e:
        session.rollback()
        logging.error(f"SetUsersProcedureException {e}")
        return False


def update_user(session: Session,
                user_id,
                **kwargs) -> bool | None:
    try:
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        session.execute(stmt)
        session.commit()
        session.close()
        return True
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        logging.warning(f"UserIntegrityError - ID:{user_id}")
        return None
    except Exception as e:
        session.rollback()
        logging.error(f"ChangeUserException {e}")
        return False
