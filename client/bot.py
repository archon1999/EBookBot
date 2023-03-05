import asyncio
import logging
import locale

from aiogram import Bot, Dispatcher, executor, types

import config
import handlers
from call_types import CallTypes

from backend.models import BotUser
from backend.enums import BotState
from backend.templates import Keys


message_handlers = {
    '/start': handlers.start_command_handler,
    Keys.SEARCH: handlers.search_key_handler,
    Keys.ABOUT: handlers.about_key_handler,
}

state_handlers = {
    BotState.SearchTextInput: handlers.search_text_message_handler,
}

bot = Bot(
    token=config.TOKEN,
    connections_limit=3,
    parse_mode='HTML',
)
dp = Dispatcher(bot)


async def update_info(user: BotUser, message: types.Message):
    user.first_name = message.from_user.first_name
    user.last_name = message.from_user.last_name
    user.username = message.from_user.username
    user.save()


@dp.message_handler(content_types=['text'])
async def message_handler(message):
    chat_id = message.chat.id
    user, success = await BotUser.get_or_create(chat_id=chat_id)
    if success:
        await update_info(user, message)

    for text, handler in message_handlers.items():
        if message.text.startswith(text):
            await handler(bot, message)
            return

    user = await BotUser.get(chat_id=chat_id)
    if user.bot_state:
        await state_handlers[user.bot_state](bot, message)


callback_query_handlers = {
    CallTypes.SearchResult: handlers.search_result_callback_query_handler,
    CallTypes.BookDetail: handlers.book_detail_callback_query_handler,
    CallTypes.BookDownload: handlers.book_download_callback_query_handler,
    CallTypes.Subscribed: handlers.subscibed_callback_query_handler,
}


@dp.callback_query_handler()
async def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, handler in callback_query_handlers.items():
        if CallType == call_type.__class__:
            await handler(bot, call)
            break


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
