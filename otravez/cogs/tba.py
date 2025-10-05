import os
from datetime import datetime

import discord
import tbapy
from discord.ext import commands

from ._utils import to_ranges

class TBA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot
        self.key = os.getenv("TBA_AUTH_KEY")
        self.tba = tbapy.TBA(self.key)

    @commands.hybrid_command(name="team", aliases=("info",), with_app_command=True)
    async def team(self, ctx: commands.Context, team: int) -> None:
        """
        Get information about a team.

        :param team: The number of the team to get information on.
        """
        data = self.tba.team("frc" + str(team))

        e = discord.Embed(color=self.bot.color,
                          title=f"FRC Team {team}",
                          url=f"https://www.thebluealliance.com/team/{team}")
        e.add_field(name="Name", value=data["nickname"])
        e.add_field(name="Location", value=f"{data.city}, {data.state_prov and f"{data.state_prov}, "}{data.country}")
        e.add_field(name="School", value=data.school_name)
        e.add_field(name="Rookie Year", value=data.rookie_year)
        if data.website is not None and data.website != "":
            e.add_field(name="Website", value=data.website)

        await ctx.send(embed=e)

    @commands.hybrid_command(name="comps", aliases=("events",), with_app_command=True)
    async def comps(self, ctx: commands.Context, team: int, year: int = datetime.now().year) -> None:
        """
        List the competitions a team attended.

        :param team: The team whose events are to be listed.
        :param year: Which year's competitions to list. Defaults to the current year.
        """

        events = self.tba.team_events(team, year)

        e = discord.Embed(color=self.bot.color,
                          title=f"{team} attended {len(events)} events in {year}")
        e.description = "\n".join([f"{ev.short_name} ({ev.event_code})" for ev in events])

        await ctx.reply(embed=e)

    @commands.hybrid_command(name="leaderboard", with_app_command=True)
    async def leaderboard(self, ctx: commands.Context, event: str, year: int = datetime.now().year) -> None:
        """
        Show the leaderboard from a given event.

        :param event: The event to show.
        :param year: Which year's leaderboard to show. Defaults to the current year.
        """

        rankings = self.tba.event_rankings(f"{year}{event}")["rankings"]

        reply = ""
        for r in rankings:
            rec = r["record"]
            total_matches = rec["wins"] + rec["losses"] + rec["ties"]
            reply += f"\n{r["rank"]}. {r["team_key"][3:]} - winrate {round(rec["wins"] / total_matches * 100, 2)}%"

        e = discord.Embed(color=self.bot.color,
                          title="Rankings")
        e.description = reply

        await ctx.reply(embed=e)

    @commands.hybrid_command(name="awards", aliases=("acolades",), with_app_command=True)
    async def awards(self, ctx: commands.Context, team: int, year: int | None = None) -> None:
        """
        Lists a team's awards.

        :param team: The team whose awards to show.
        :param year: Which year's awards to show. If none, lists all awards.
        """

        if year:
            awards = self.tba.team_awards(team, year=year)
        else:
            awards = self.tba.team_awards(team)

        reply = ""

        for i, aw in enumerate(awards):
            if len(reply) >= 1000:
                reply += f"\n...and {len(awards)-i} more."
                break

            reply += f"\n- {aw["name"]} ({aw["year"]})"

        e = discord.Embed(color=self.bot.color,
                          title=f"{team}'s awards {f"in {year}" if year else ""}")
        e.description = reply

        await ctx.reply(embed=e)

    @commands.hybrid_command(name="alliances", with_app_command=True)
    async def alliances(self, ctx: commands.Context, event: str, year: int = datetime.now().year) -> None:
        """
        Shows the list of alliances from a given event.

        :param event: The code of the event to list alliances from.
        :param year: The year from which to show alliances. Defaults to current year.
        """

        alliances = self.tba.event_alliances(f"{year}{event}")

        reply = ""

        for i, a in enumerate(alliances):
            # Add the alliance to the reply, removing the "frc" at the beginning of
            # each team's number. At the end, if the alliance won their event, add
            # (won).
            reply += f"\n{i}. {
                ", ".join([p[3:] for p in a["picks"]])
            }{
                " (**won**)" if a["status"]["status"] == "won" else ""
            }"

        e = discord.Embed(color=self.bot.color, title="Alliances")
        e.description = reply

        await ctx.reply(embed=e)

    @commands.hybrid_command(name="years", with_app_command=True)
    async def years(self, ctx: commands.Context, team: int) -> None:
        """
        Lists the years a given team was/is active.

        :param team: The team whose active years to get.
        """

        years = self.tba.team_years(team)
        year_ranges = list(to_ranges(years))

        reply = ""
        for r in year_ranges:
            if r[1] == r[0]:
                reply += f"\n- {r[0]}"
                continue

            reply += f"\n- {r[0]}-{r[1]}"

        e = discord.Embed(color=self.bot.color,
                          title=f"{team} was active in the following years:")
        e.description = reply

        await ctx.reply(embed=e)

async def setup(bot):
    """Adds the cog to the bot."""
    await bot.add_cog(TBA(bot))
