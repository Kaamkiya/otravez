import os

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
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

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
        await ctx.reply("Invalid team number. Usage: ;stat [teamnum]")

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
    try:
        team, year, *args = args.split()
        events = tba.team_events(int(team), int(year))
    except ValueError:
        await ctx.reply("Usage: ;comps [team] [year]")

    await ctx.reply(f"{len(events)}: {"\n".join(f"{ev.short_name} ({ev.event_code})" for ev in events)}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
