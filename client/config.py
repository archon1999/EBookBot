import os
import sys
import asyncio

import dotenv
from tortoise import Tortoise

dotenv.load_dotenv('../.env')

TOKEN = os.getenv('BOT_TOKEN')

PARENT_PACKAGE = '..'
SERVER_PACKAGE = 'server'
PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
SERVER_DIR = os.path.join(PARENT_DIR, SERVER_PACKAGE)

sys.path.append(SERVER_DIR)
sys.path.append(PARENT_DIR)


async def init():
    await Tortoise.init(
        db_url='sqlite://../server/db.sqlite',
        modules={'models': ['backend.models']}
    )

asyncio.run(init())
