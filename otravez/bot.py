import os

import discord
from discord.ext import commands

class OtraVez(commands.Bot):
    """A simple bot for getting FRC information about teams, events, and more."""

    color = discord.Color.from_str("#ccaaff")

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=";",
                         description="A simple bot for getting FRC information about teams, events, and more.",
                         intents=intents,
                         case_insenstive=True,
                         activity=discord.Game("meep morp"))

        self.color = discord.Color.from_str("#ccaaff")

    async def setup_hook(self) -> None:
        await self.load_cogs()

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")

