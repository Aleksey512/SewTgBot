import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from db.conn import init_models, session
from db.utils import add_user
from handlers.auth import router as auth_router
from handlers.callbacks import router as callbacks_router
from handlers.commands import router as commands_router
from handlers.directors import router as directors_router
from handlers.employee import router as employee_router
from handlers.profile import router as profile_router
from middlewares.middleware import CheckAuthCallbackMiddleware
from ui_commands import set_ui_commands

TG_TOKEN = os.getenv("TG_TOKEN")

router = Router()


async def main() -> None:
    init_models()
    add_user(session,
             name='Admin',
             surname='Adminov',
             login=f"{os.getenv('ADMIN_LOGIN')}",
             password=f"{os.getenv('ADMIN_PASSWORD')}",
             role="admin",
             )
    add_user(session,
             name='Директор',
             surname='Директор',
             login=f"director1",
             password=f"{os.getenv('DIRECTOR_PASSWORD')}",
             role="director",
             )
    add_user(session,
             name='Директор2',
             surname='Директор2',
             login=f"director2",
             password=f"{os.getenv('DIRECTOR_PASSWORD')}",
             role="director",
             )
    add_user(session,
             name='Директор3',
             surname='Директор3',
             login=f"director3",
             password=f"{os.getenv('DIRECTOR_PASSWORD')}",
             role="director",
             )
    bot = Bot(TG_TOKEN, parse_mode="HTML")

    # storage = RedisStorage.from_url(
    #     f'{os.getenv("REDIS_HOST")}://redis:{os.getenv("REDIS_PORT")}/0', connection_kwargs={"decode_responses": True})
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Принудительно настраиваем фильтр на работу только в чатах один-на-один с ботом
    dp.message.filter(F.chat.type == "private")

    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.callback_query.middleware(CheckAuthCallbackMiddleware())

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(auth_router)
    dp.include_router(profile_router)
    dp.include_router(directors_router)
    dp.include_router(employee_router)

    # Set bot commands in UI
    await set_ui_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
