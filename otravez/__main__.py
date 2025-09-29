import os

from dotenv import load_dotenv

from bot import OtraVez

load_dotenv()

bot = OtraVez()
bot.run(os.getenv("DISCORD_TOKEN"))
