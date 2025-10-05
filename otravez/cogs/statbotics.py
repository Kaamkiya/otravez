import os
from datetime import datetime

import discord
from discord.ext import commands
from statbotics import Statbotics

class SB(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()

        self.bot = bot
        self.sb = Statbotics()

    @commands.hybrid_command(name="epa", with_app_command=True)
    async def epa(self, ctx: commands.Context, team: int, event: str, year: int = datetime.now().year) -> None:
        """
        Shows a team's EPA at a given event in a given year.

        :param team: The team whose EPA to show
        :param event: Which event to show their EPA at
        :param year: Which year to show their event EPA at
        """

        data = self.sb.get_team_event(team, f"{year}{event}")

        e = discord.Embed(color=self.bot.color,
                          title=f"{team} at {data["event_name"]} in {year}")
        e.add_field(name="EPA", value=data["epa"]["breakdown"]["total_points"])
        e.add_field(name="Win Rate", value=f"{round(data["record"]["total"]["winrate"] * 100, 2)}%")

        await ctx.reply(embed=e)

    @commands.command(name="event", with_app_command=True)
    async def event(self, ctx: commands.Context, event: str, year: int = datetime.now().year) -> None:
        """
        Shows information about an event.

        :param event: The code of the event to show info about.
        :param year: Which year's information to show.
        """

        data = self.sb.get_event(f"{year}{event}")

        e = discord.Embed(color=self.bot.color,
                          title=data["name"])
        e.add_field(name="Type", value=data["type"])
        e.add_field(name="Week", value=data["week"])
        e.add_field(name="District", value=data["district"])
        e.add_field(name="Quals", value=data["qual_matches"])
        e.add_field(name="Teams", value=data["num_teams"])
        e.add_field(name="FirstInspires", value=f"<https://frc-events.firstinspires.org/{year}/{event}>")

        if data.get("video", False):
            e.add_field(name="Stream", value=f"<{data["video"]}>")

        await ctx.reply(embed=e)

async def setup(bot):
    """Adds the cog to the bot."""
    await bot.add_cog(SB(bot))
