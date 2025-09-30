import datetime
import platform

import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Checks if the robot is online and calculates response time."""

        res = await ctx.reply("pong!")
        delay = res.created_at - ctx.message.created_at

        await res.edit(content=res.content + f" {round(delay.microseconds / 1000)}ms")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(name="botinfo")
    async def botinfo(self, ctx: commands.Context) -> None:
        uptime = datetime.datetime.now(datetime.UTC) - self.bot.starttime
        uptime = round(uptime.total_seconds())

        e = discord.Embed(color=self.bot.color, title="Bot Info")
        e.add_field(name="Uptime", value=f"{uptime} seconds")
        e.add_field(name="Python version", value=platform.python_version())
        e.add_field(name="Library version", value=f"{discord.__version__}")
        e.add_field(name="WebSocket latency", value=f"{self.bot.latency * 1000:.2f}ms")
        e.add_field(name="Guild count", value=f"{len(self.bot.guilds)}")
        e.add_field(name="User count", value=f"{sum(g.member_count for g in self.bot.guilds)}")
        e.add_field(name="Cog count", value=len(self.bot.cogs))

        await ctx.reply(embed=e)

async def setup(bot):
    """Adds the cog to the bot."""
    await bot.add_cog(General(bot))
