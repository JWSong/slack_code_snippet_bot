import asyncio

from config import DEBUG, TOKEN
from snippet_bot import Bot

bot = Bot(TOKEN)

loop = asyncio.new_event_loop()
loop.set_debug(DEBUG)
asyncio.get_event_loop().run_until_complete(bot.run())
asyncio.get_event_loop().run_forever()
loop.close()
