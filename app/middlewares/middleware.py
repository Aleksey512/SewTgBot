from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


# Это будет inner-мидлварь на сообщения
class CheckAuthMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if data['state']:
            state_data = await data['state'].get_data()
            if 'user' in state_data:
                return await handler(event, data)
            await event.answer(
                "Вы не вошли в систему!",
                show_alert=True
            )
            return


class CheckAuthCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if data['state']:
            state_data = await data['state'].get_data()
            if 'user' in state_data:
                return await handler(event, data)
            await event.answer(
                "Вы не вошли в систему!",
                show_alert=True
            )
            return
