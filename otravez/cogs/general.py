from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Checks if the robot is online and calculates response time."""

        res = await ctx.reply("pong!")
        delay = res.created_at - ctx.message.created_at

        await res.edit(content=res.content + f" {round(delay.microseconds / 1000)}ms")

async def setup(bot):
    """Adds the cog to the bot."""
    await bot.add_cog(General(bot))
