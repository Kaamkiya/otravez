import os
from datetime import datetime

import discord
import logging
import tbapy
import statbotics
from discord.ext import commands
from dotenv import load_dotenv

from utils import to_ranges

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

tba = tbapy.TBA(os.getenv("TBA_AUTH_KEY"))
sb = statbotics.Statbotics()

bot = commands.Bot(command_prefix=";", intents=intents)

@bot.event
async def on_ready():
    print(f"Yay bot has started! Named {bot.user.name}")

@bot.command()
async def ping(ctx):
    """
        Responds to a message starting with ";ping" by saying "pong".
    """
    await ctx.send("pong")

@bot.command()
async def stat(ctx, *, args):
    team, *args = args.split()

    try:
        team = int(team)
    except ValueError:
        await ctx.reply("Invalid team number. Usage: ;stat [team]")
        return

    data = sb.get_team(team)

    years = tba.team_years(team)
    year_ranges = list(to_ranges(years))
    years_str = ""

    for r in year_ranges:
        if r[1] == r[0]:
            years_str += f"{r[0]}, "
            continue

        years_str += f"{r[0]}-{r[1]}, "

    await ctx.reply(f"""{team} - {data["name"]}:
years active: {years_str}
win/loss ratio: {round(data["record"]["winrate"] * 100, 2)}%
""")

@bot.command()
async def info(ctx, *, args):
    """
        Returns basic facts about a team, like their name, website, and school.
    """
    team_number, *args = args.split()

    try:
        int(team_number)
    except ValueError:
        await ctx.reply("Invalid team number. Usage: ;stat [team]")
        return

    data = tba.team("frc" + team_number)

    if data.get("nickname", None) is None:
        await ctx.reply("No such team.")
        return

    await ctx.reply(f"""
name: {data.nickname}
location: {data.city}, {data.state_prov and f"{data.state_prov}, "}{data.country}
school: {data.school_name}
rookie year: {data.rookie_year}
website: {data.website}""")

@bot.command(aliases=["events"])
async def comps(ctx, *, args):
    """
        Sends the competitions a given team attended in the given (or default)
        year.
    """

    try:
        team, *args = args.split()

        # if the user provided a year, use that, otherwise default to this year
        year = int(args[0]) if len(args) > 0 else datetime.now().year

        events = tba.team_events(int(team), year)
    except ValueError:
        await ctx.reply("Usage: ;comps [team] [optional: year]")

    reply = f"{len(events)} in {year}:"
    for ev in events:
        reply += f"\n- {ev.short_name} ({ev.event_code})"

    await ctx.reply(reply)

@bot.command()
async def years(ctx, *, args):
    """
        Sends a list of years that a team participated in FRC.
    """

    try:
        team, *_ = args.split()

        years = tba.team_years(int(team))
    except ValueError:
        await ctx.reply("Usage: ;years [team]")

    year_ranges = list(to_ranges(years))

    reply = "Years:"
    for r in year_ranges:
        if r[1] == r[0]:
            reply += f"\n- {r[0]}"
            continue

        reply += f"\n- {r[0]}-{r[1]}"

    await ctx.reply(reply)

@bot.command()
async def epa(ctx, *, args):
    """
        Accepts an event code and team number, and optional year, and returns
        the EPA and win rate of the team.

        For example:
            ;epa 8884 onosh
    """
    team, ev_shortcode, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year

    try:
        team = int(team)
    except ValueError:
        await ctx.reply("Invalid team number.")

    try:
        data = sb.get_team_event(team, f"{year}{ev_shortcode}")
    except:
        await ctx.reply("Failed to get event data")

    epa = data["epa"]["breakdown"]["total_points"]
    winrate = data["record"]["total"]["winrate"]

    await ctx.reply(f"{team} at {data["event_name"]}\nEPA: {epa}\nWin rate: {round(winrate * 100, 2)}%")

@bot.command()
async def leaderboard(ctx, *, args):
    """
        Accepts an event code and year, and returns the leaderboard.
    """

    ev_shortcode, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year

    try:
        rankings = tba.event_rankings(f"{year}{ev_shortcode}")["rankings"]
    except:
        await ctx.reply("Doesn't seem like there are rankings for this event...")
        return

    reply = "Rankings:"

    for r in rankings:
        rec = r["record"]
        total_matches = rec["wins"] + rec["losses"] + rec["ties"]
        reply += f"\n{r["rank"]}. {r["team_key"][3:]} - winrate {round(rec["wins"] / total_matches * 100, 2)}%"

    await ctx.reply(reply)

@bot.command()
async def event(ctx, *, args):
    """
        Accepts an event code and year and returns data about the event.
    """

    ev_code, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year

    data = sb.get_event(f"{year}{ev_code}")

    await ctx.reply(f"""{data["name"]}
Type: {data["type"]}
Week: {data["week"]}
District: {data["district"]}
Quals: {data["qual_matches"]}
Teams: {data["num_teams"]}
{f"Streams: <{data["video"]}>" if data.get("video", None) is not None else ""}
FirstInspires: <https://frc-events.firstinspires.org/{year}/{ev_code}>""")

@bot.command()
async def searchevent(ctx, *, args):
    """
        Accepts a year, country, state, district, week, and limit, and
        returns a list of events.
    """

    args = args.split()
    year = datetime.now().year
    country = None
    state = None
    district = None
    week = None
    limit = 10

    for arg in args:
        try:
            key, value = arg.split("=")
        except:
            await ctx.reply("Send values as key=value, eg year=2025")
            return

        value = value.strip()
        match key.strip():
            case "year": year = int(value)
            case "country": country = value
            case "state": state = value
            case "district": district = value
            case "week": week = int(value)
            case "limit":
                value = int(value)
                if value > limit:
                    await ctx.reply(f"Maximum limit: {limit}")
                    return
                limit = value

    data = sb.get_events(year=year,
                         country=country,
                         state=state,
                         district=district,
                         week=week,
                         limit=limit)

    reply = ""

    for event in data:
        reply += f"\n{event["name"]} ({event["key"][4:]})"

    await ctx.reply(reply)

@bot.command()
async def awards(ctx, *, args):
    """
        Accepts a team number and returns the awards the team has won.
    """

    args = args.split()
    team = int(args[0]) if len(args) > 0 else datetime.now().year

    awards = tba.team_awards(team)

    reply = "Team Awards:"

    for i, aw in enumerate(awards):
        if len(reply) >= 1950:
            reply += f"\n...and {len(awards)-i} more."
            break

        reply += f"\n- {aw["name"]} ({aw["year"]})"

    await ctx.reply(reply)

@bot.command()
async def alliances(ctx, *, args):
    """
        Accepts an event code and year, and returns a list of alliances.
    """

    ev_shortcode, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year
    
    alliances = tba.event_alliances(f"{year}{ev_shortcode}")

    reply = "Alliances:"

    for a in alliances:
        # Add the alliance to the reply, removing the "frc" at the beginning of
        # each team's number. At the end, if the alliance won their event, add
        # (won).
        reply += f"\n{
            a["name"]
        }: {
            ", ".join([p[3:] for p in a["picks"]])
        }{
            " (**won**)" if a["status"]["status"] == "won" else ""
        }"

    await ctx.reply(reply)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
