from backend.models import Template
from asgiref.sync import async_to_sync


class Messages():
    START_COMMAND_HANDLER = async_to_sync(Template.messages.get)(id=2).gettext()
    SEARCH = async_to_sync(Template.messages.get)(id=7).gettext()
    SEARCHING = async_to_sync(Template.messages.get)(id=8).gettext()
    SEARCH_RESULT = async_to_sync(Template.messages.get)(id=9).gettext()
    BOOK_LIST_INFO = async_to_sync(Template.messages.get)(id=10).gettext()
    BOOK_DETAIL = async_to_sync(Template.messages.get)(id=12).gettext()
    MANDATORY_SUBSCRIPTION = async_to_sync(Template.messages.get)(id=16).gettext()
    NOT_SUBSCRIBED = async_to_sync(Template.messages.get)(id=18).gettext()
    SUBSCRIBED_SUCCESS = async_to_sync(Template.messages.get)(id=19).gettext()
    BOOK_DOWNLOADING = async_to_sync(Template.messages.get)(id=20).gettext()
    ABOUT = async_to_sync(Template.messages.get)(id=21).gettext()


class Keys():
    MENU = async_to_sync(Template.keys.get)(id=3).gettext()
    SEARCH = async_to_sync(Template.keys.get)(id=4).gettext()
    FAVORITES = async_to_sync(Template.keys.get)(id=5).gettext()
    ABOUT = async_to_sync(Template.keys.get)(id=6).gettext()
    BACK = async_to_sync(Template.keys.get)(id=13).gettext()
    BY_AUTHOR = async_to_sync(Template.keys.get)(id=14).gettext()
    TO_FAVORITES = async_to_sync(Template.keys.get)(id=15).gettext()
    SUBSCRIBED = async_to_sync(Template.keys.get)(id=17).gettext()
    ADD_TO_GROUP = async_to_sync(Template.keys.get)(id=22).gettext()


class Smiles():
    NEXT_PAGE = async_to_sync(Template.smiles.get)(id=1).gettext()
    PREV_PAGE = async_to_sync(Template.smiles.get)(id=11).gettext()
