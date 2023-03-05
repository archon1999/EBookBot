from enum import Enum, IntEnum


class Status(IntEnum):
    on = 1
    off = 0


class Action(str, Enum):
    create = "create"
    delete = "delete"
    edit = "edit"


class TemplateType(IntEnum):
    Message = 1
    Key = 2
    Smile = 3


class BotState(IntEnum):
    Nothing = 0
    SearchTextInput = 1


class BookFormat(str, Enum):
    FB2 = 'fb2'
    EPUB = 'epub'
    MOBI = 'mobi'
    TXT = 'txt'
