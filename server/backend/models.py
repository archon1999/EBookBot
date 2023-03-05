import datetime

from tortoise import Model, fields
from tortoise.signals import post_save, post_delete, pre_save
from tortoise.manager import Manager
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

from backend.enums import Status, TemplateType, BotState
from fastapi_admin.models import AbstractAdmin


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(description="Last Login",
                                      default=datetime.datetime.now)
    email = fields.CharField(max_length=200, default="")
    avatar = fields.CharField(max_length=200, default="")
    intro = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}#{self.username}'


class BotUser(Model):
    chat_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=255,
                                null=True,
                                blank=True)
    first_name = fields.CharField(max_length=255,
                                  null=True,
                                  blank=True)
    last_name = fields.CharField(max_length=255,
                                 null=True,
                                 blank=True)
    bot_state = fields.IntEnumField(BotState, default=BotState.Nothing)


class Book(Model):
    books = Manager()
    book_id = fields.IntField()
    title = fields.CharField(max_length=255)
    img_link = fields.CharField(max_length=255)
    tags = fields.CharField(max_length=255)
    public_year = fields.IntField()
    description = fields.TextField()

    def __str__(self):
        return self.title


class BookAuthor(Model):
    book = fields.ForeignKeyField('models.Book', related_name='authors')
    author_name = fields.CharField(max_length=255)
    author_id = fields.IntField()


class FavoriteBook(Model):
    user = fields.ForeignKeyField('models.BotUser',
                                  related_name='favorite_books')
    book = fields.ForeignKeyField('models.Book')


class MandatorySubscription(Model):
    channel = fields.CharField(max_length=255)


class Config(Model):
    label = fields.CharField(max_length=200)
    key = fields.CharField(max_length=20, unique=True,
                           description="Unique key for config")
    value = fields.JSONField()
    status: Status = fields.IntEnumField(Status, default=Status.on)


def filter_tag(tag: Tag, ol_number=None):
    if isinstance(tag, NavigableString):
        text = tag
        text = text.replace('<', '&#60;')
        text = text.replace('>', '&#62;')
        return text

    html = str()
    li_number = 0
    for child_tag in tag:
        if tag.name == 'ol':
            if child_tag.name == 'li':
                li_number += 1
        else:
            li_number = None

        html += filter_tag(child_tag, li_number)

    format_tags = ['strong', 'em', 'pre', 'b', 'u', 'i', 'code']
    if tag.name in format_tags:
        return f'<{tag.name}>{html}</{tag.name}>'

    if tag.name == 'a':
        return f"""<a href="{tag.get("href")}">{tag.text}</a>"""

    if tag.name == 'li':
        if ol_number:
            return f'{ol_number}. {html}'
        return f'•  {html}'

    if tag.name == 'br':
        html += '\n'

    if tag.name == 'span':
        styles = tag.get_attribute_list('style')
        if 'text-decoration: underline;' in styles:
            return f'<u>{html}</u>'

    if tag.name == 'ol' or tag.name == 'ul':
        return '\n'.join(map(lambda row: f'   {row}', html.split('\n')))

    return html


def filter_html(html: str):
    soup = BeautifulSoup(html, 'lxml')
    return filter_tag(soup)


class MessageManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=TemplateType.Message)


class KeyManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=TemplateType.Key)


class SmileManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=TemplateType.Smile)


class Template(Model):
    templates = Manager()
    messages = MessageManager()
    keys = KeyManager()
    smiles = SmileManager()

    type = fields.IntEnumField(TemplateType)
    title = fields.CharField(max_length=100)
    body = fields.TextField()

    def gettext(self):
        return filter_html(self.body)


async def generate_code():
    code_text = str()
    code_text += 'from backend.models import Template\n'
    code_text += 'from asgiref.sync import async_to_sync\n'
    code_text += '\n\nclass Messages():\n'
    async for message in Template.messages.all():
        code_text += f'    {message.title} = async_to_sync('
        code_text += f'Template.messages.get)(id={message.id}).gettext()\n'

    code_text += '\n\nclass Keys():\n'
    async for key in Template.keys.all():
        code_text += f'    {key.title} = async_to_sync('
        code_text += f'Template.keys.get)(id={key.id}).gettext()\n'

    code_text += '\n\nclass Smiles():\n'
    async for smile in Template.smiles.all():
        code_text += f'    {smile.title} = async_to_sync('
        code_text += f'Template.smiles.get)(id={smile.id}).gettext()\n'

    return code_text


@pre_save(Template)
async def template_pre_save(sender, instance, *args, **kwargs):
    if await Template.filter(id=instance.id).exists():
        template = await Template.get(id=instance.id)
        instance.type = template.type


@post_save(Template)
async def template_post_save(*args, **kwargs):
    template_file = 'backend/templates.py'
    with open(template_file, 'w') as file:
        file.write(await generate_code())


@post_delete(Template)
async def template_post_delete(*args, **kwargs):
    template_file = 'backend/templates.py'
    with open(template_file, 'w') as file:
        file.write(await generate_code())
