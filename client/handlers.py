from aiogram import Bot, types
from django.core.paginator import Paginator

from backend.enums import BotState
from backend.models import BotUser, MandatorySubscription
from backend.templates import Messages, Keys
from client.call_types import CallTypes
from parser import flibusta

import utils


BOOKS_PER_PAGE = 5


async def start_command_handler(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add(Keys.SEARCH, Keys.FAVORITES)
    keyboard.add(Keys.ABOUT)
    await bot.send_message(chat_id, Messages.START_COMMAND_HANDLER,
                           reply_markup=keyboard)


async def search_key_handler(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, Messages.SEARCH)
    user = await BotUser.get(chat_id=chat_id)
    user.bot_state = BotState.SearchTextInput
    await user.save()


async def about_key_handler(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    user = await bot.get_me()
    add_to_chat_button = types.InlineKeyboardButton(
        text=Keys.ADD_TO_GROUP,
        url=f'https://t.me/{user.username}?startgroup=true'
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(add_to_chat_button)
    await bot.send_message(chat_id, Messages.ABOUT,
                           reply_markup=keyboard)


async def search_text_message_handler(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    search_text = message.text
    text = Messages.SEARCHING.format(search_text=search_text)
    message = await bot.send_message(chat_id, text)
    user = await BotUser.get(chat_id=chat_id)
    user.bot_state = BotState.Nothing
    await user.save()
    await bot.delete_message(chat_id, message.message_id)
    call_type = CallTypes.SearchResult(page=1, q=search_text)
    message.data = CallTypes.make_data(call_type)
    await search_result_callback_query_handler(bot, message)


async def search_result_callback_query_handler(bot: Bot, call: types.CallbackQuery):
    if hasattr(call, 'message'):
        chat_id = call.message.chat.id
    else:
        chat_id = call.chat.id

    call_type = CallTypes.parse_data(call.data)
    search_text = call_type.q
    page_number = call_type.page
    books = await flibusta.get_book_list(search_text)
    paginator = Paginator(books, BOOKS_PER_PAGE)
    page = paginator.get_page(page_number)
    books_info = str()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    keyboard = utils.make_page_keyboard(
        page=page,
        CallType=CallTypes.SearchResult,
        q=search_text,
    )
    buttons = []
    for index, book in enumerate(page, 1):
        book = await utils.get_book(book.id)
        books_info += Messages.BOOK_LIST_INFO.format(
            index=index,
            book_title=book.title,
            author_name=utils.text_to_code(book.author_name),
            year_public=book.year_public or '',
        ) + '\n\n'
        buttons.append(utils.make_inline_button(
            text=str(index),
            CallType=CallTypes.BookDetail,
            q=search_text,
            book_id=book.id,
        ))

    keyboard.add(*buttons)
    text = Messages.SEARCH_RESULT.format(
        search_text=search_text,
        books_info=books_info,
    )

    if hasattr(call, 'message'):
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(chat_id, text,
                               reply_markup=keyboard)


async def book_detail_callback_query_handler(bot: Bot, call: types.CallbackQuery):
    chat_id = call.message.chat.id
    call_type = CallTypes.parse_data(call.data)
    search_text = call_type.q
    book_id = call_type.book_id
    book = await utils.get_book(book_id)
    book_detail = Messages.BOOK_DETAIL.format(
        book_title=book.title,
        author_name=book.author_name,
        year_public=book.year_public,
        tags=book.tags,
        description=book.description,
    )
    back_button = utils.make_inline_button(
        text=Keys.BACK,
        CallType=CallTypes.SearchResult,
        page=1,
        q=search_text,
    )
    by_author_button = utils.make_inline_button(
        text=Keys.BY_AUTHOR,
        CallType=CallTypes.SearchResultByAuthor,
        page=1,
        author_id=book.author_id,
    )
    to_favorites_button = utils.make_inline_button(
        text=Keys.TO_FAVORITES,
        CallType=CallTypes.ToFavorites,
        book_id=book.id,
    )
    download_buttons = []
    for name, format, url in book.download_formats:
        download_button = utils.make_inline_button(
            text=name,
            CallType=CallTypes.BookDownload,
            id=book.id,
            f=format,
            u=url,
        )
        download_buttons.append(download_button)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(back_button)
    keyboard.add(by_author_button, to_favorites_button)
    keyboard.add(*download_buttons)
    await bot.edit_message_text(
        text=book_detail,
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
    )


async def book_download_callback_query_handler(bot: Bot, call: types.CallbackQuery):
    chat_id = call.message.chat.id
    call_type = CallTypes.parse_data(call.data)
    ok = True
    async for obj in MandatorySubscription.all():
        channel = obj.channel
        try:
            user = await bot.get_chat_member(channel, call.from_user.id)
            if not user or user.status == 'left':
                ok = False
                break
        except Exception:
            pass

    if not ok:
        keyboard = types.InlineKeyboardMarkup()
        for index, obj in enumerate(await MandatorySubscription.all(), 1):
            channel = obj.channel
            channel_button = types.InlineKeyboardButton(
                text=f'Канал №{index}',
                url=f'https://t.me/{channel.removeprefix("@")}',
            )
            keyboard.add(channel_button)

        subscibed_button = utils.make_inline_button(
            text=Keys.SUBSCRIBED,
            CallType=CallTypes.Subscribed,
        )
        keyboard.add(subscibed_button)
        await bot.send_message(chat_id, Messages.MANDATORY_SUBSCRIPTION,
                               reply_markup=keyboard)
        return

    format = call_type.f
    url = call_type.u
    book_id = call_type.id
    print(format, url, book_id)
    await bot.answer_callback_query(call.id, Messages.BOOK_DOWNLOADING)
    content = await flibusta.book_download(url)
    filename = f'{book_id}.{format}'
    with open(filename, 'wb') as file:
        file.write(content)

    await bot.send_document(chat_id, types.InputFile(filename),
                            disable_content_type_detection=True)


async def subscibed_callback_query_handler(bot: Bot, call: types.CallbackQuery):
    async for obj in MandatorySubscription.all():
        channel = obj.channel
        try:
            user = await bot.get_chat_member(channel, call.from_user.id)
            if not user or user.status == 'left':
                await bot.answer_callback_query(call.id, Messages.NOT_SUBSCRIBED, True)
                return
        except Exception:
            pass

    await bot.answer_callback_query(call.id, Messages.SUBSCRIBED_SUCCESS, True)
