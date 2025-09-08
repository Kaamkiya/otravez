import os
from datetime import datetime

import discord
import logging
import tbapy
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

tba = tbapy.TBA(os.getenv("TBA_AUTH_KEY"))

bot = commands.Bot(command_prefix=";", intents=intents)

@bot.event
async def on_ready():
    print(f"Yay bot has started! Named {bot.user.name}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    if "otra vez" in msg.content.lower():
        await msg.channel.send(f"{msg.author.mention} oop I was summoned")

    await bot.process_commands(msg)

@bot.command()
async def ping(ctx):
    """
        Responds to a message starting with ";ping" by saying "pong".
    """
    await ctx.send("pong")

@bot.command()
async def stat(ctx, *, args):
    """
        Returns basic facts about a team, like their name, website, and school.
    """
    team_number, *args = args.split()

    try:
        int(team_number)
    except ValueError:
        await ctx.reply("Invalid team number. Usage: ;stat [team]")

    data = tba.team("frc" + team_number)

    if data.get("nickname", None) is None:
        await ctx.reply("No such team.")

    await ctx.reply(f"""
name: {data.nickname}
location: {data.city}, {data.state_prov and f"{data.state_prov}, "}{data.country}
school: {data.school_name}
rookie year: {data.rookie_year}
website: {data.website}""")

@bot.command()
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

    reply = "Years:"
    for year in years:
        reply += f"\n- {year}"

    await ctx.reply(reply)

@bot.command()
async def epa(ctx, *, args):
    """
        Accepts an event code and team number, and returns the position of the
        given team on the event leaderboard.

        For example:
            ;epa onosh 8884
        Would return:
            1. team in first | epa
            ...
            14. 8884 | epa
            ...
            40. team in last | epa
    """
    pass

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
