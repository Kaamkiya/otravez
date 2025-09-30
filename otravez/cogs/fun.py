import os
import urllib.parse

import aiohttp
import discord
import tbapy
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="weather")
    async def teamweather(self, ctx: commands.Context, team: int) -> None:
        """
        Fetches the weather for a given team's location.

        :param team: The team whose weather information to get.
        """

        # Get the location of the team according to TBA
        data = tbapy.TBA(os.getenv("TBA_AUTH_KEY")).team(f"frc{team}")
        location = f"{data.city}+{data.state_prov}+{data.country}"

        # Get the JSON weather data
        url = "https://wttr.in/" + urllib.parse.quote(location, safe="") + "?format=j1"
        async with ctx.typing(), (s := aiohttp.ClientSession()).get(url) as res:
            weather = await res.json()
        await s.close()

        weather = weather["current_condition"][0]

        # Format and send the weather
        e = discord.Embed(color=self.bot.color, title=f"{team}'s Weather")
        e.description = f"It's a {
                weather["weatherDesc"][0]["value"].lower()
            } {weather["temp_C"]} degrees celsius for them!"

        await ctx.reply(embed=e)

async def setup(bot):
    await bot.add_cog(Fun(bot))
