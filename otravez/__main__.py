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

bot_color = discord.Colour.from_str("#1e1e2e")
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

    for i, r in enumerate(year_ranges):
        if r[1] == r[0]:
            years_str += f"{r[0]}"
        else:
            years_str += f"{r[0]}-{r[1]}"

        if i != len(year_ranges) - 1:
            years_str += ", "

    e = discord.Embed(color=bot_color,
                      title=f"FRC Team {team} Stats")
    e.add_field(name="Years", value=years_str)
    e.add_field(name="Win/Loss Ratio", value=f"{round(data["record"]["winrate"] * 100, 2)}%")

    await ctx.reply(embed=e)

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

    e = discord.Embed(color=bot_color,
                      title=f"FIRST Robotics Team {team_number}",
                      url=f"https://www.thebluealliance.com/team/{team_number}")
    e.add_field(name="Name", value=data.nickname)
    e.add_field(name="Location", value=f"{data.city}, {data.state_prov and f"{data.state_prov}, "}{data.country}")
    e.add_field(name="School", value=data.school_name)
    e.add_field(name="Rookie Year", value=data.rookie_year)
    if data.website is not None and data.website != "":
        e.add_field(name="Website", value=data.website)

    await ctx.send(embed=e)

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

    e = discord.Embed(color=bot_color,
                      title=f"{team} attended {len(events)} events in {year}")
    e.description = "\n".join([f"{ev.short_name} ({ev.event_code})" for ev in events])

    await ctx.reply(embed=e)

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

    reply = ""
    for r in year_ranges:
        if r[1] == r[0]:
            reply += f"\n- {r[0]}"
            continue

        reply += f"\n- {r[0]}-{r[1]}"

    e = discord.Embed(color=bot_color,
                      title=f"{team} was active in the following years:")
    e.description = reply

    await ctx.reply(embed=e)

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

    e = discord.Embed(color=bot_color,
                      title=f"{team} at {data["event_name"]} in {year}")
    e.add_field(name="EPA", value=data["epa"]["breakdown"]["total_points"])
    e.add_field(name="Win Rate", value=f"{round(data["record"]["total"]["winrate"] * 100, 2)}%")

    await ctx.reply(embed=e)

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

    e = discord.Embed(color=bot_color,
                      title="Rankings")
    e.description = reply

    await ctx.reply(embed=e)

@bot.command()
async def event(ctx, *, args):
    """
        Accepts an event code and year and returns data about the event.
    """

    ev_code, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year

    data = sb.get_event(f"{year}{ev_code}")

    e = discord.Embed(color=bot_color,
                      title=data["name"])
    e.add_field(name="Type", value=data["type"])
    e.add_field(name="Week", value=data["week"])
    e.add_field(name="District", value=data["district"])
    e.add_field(name="Quals", value=data["qual_matches"])
    e.add_field(name="Teams", value=data["num_teams"])
    e.add_field(name="FirstInspires", value=f"<https://frc-events.firstinspires.org/{year}/{ev_code}>")

    if data.get("video", False):
        e.add_field(name="Stream", value=f"<{data["video"]}>")

    await ctx.reply(embed=e)

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
    limit = 30

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

    try:
        data = sb.get_events(year=year,
                             country=country,
                             state=state,
                             district=district,
                             week=week,
                             limit=limit)
    except:
        await ctx.reply("Failed to get events.")
        return

    e = discord.Embed(color=bot_color,
                      title=f"Found {len(data)} events")
    e.description = "\n".join([f"{ev["name"]} ({ev["key"][4:]})" for ev in data])

    await ctx.reply(embed=e)

@bot.command()
async def awards(ctx, *, args):
    """
        Accepts a team number and returns the awards the team has won.
    """

    team, *args = args.split()
    try:
        team = int(team)
    except ValueError:
        await ctx.reply("Requires a team number")
        return

    year = int(args[0]) if len(args) > 0 else None

    if year:
        awards = tba.team_awards(team, year=year)
    else:
        awards = tba.team_awards(team)

    reply = ""

    for i, aw in enumerate(awards):
        if len(reply) >= 1000:
            reply += f"\n...and {len(awards)-i} more."
            break

        reply += f"\n- {aw["name"]} ({aw["year"]})"

    e = discord.Embed(color=bot_color,
                      title=f"{team}'s awards {f"in {year}" if year else ""}")
    e.description = reply

    await ctx.reply(embed=e)

@bot.command()
async def alliances(ctx, *, args):
    """
        Accepts an event code and year, and returns a list of alliances.
    """

    ev_shortcode, *args = args.split()
    year = int(args[0]) if len(args) > 0 else datetime.now().year
    
    try:
        alliances = tba.event_alliances(f"{year}{ev_shortcode}")
    except:
        await ctx.send("No alliance data found")
        return

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

    e = discord.Embed(color=bot_color, title="Alliances")
    e.description = reply

    await ctx.reply(embed=e)

bot.run(token, log_handler=handler, log_level=logging.INFO)
