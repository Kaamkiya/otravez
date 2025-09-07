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

tba_client = tbapy.TBA(os.getenv("TBA_AUTH_KEY"))

bot = commands.Bot(command_prefix=";", intents=intents)

@bot.event
async def on_ready():
    print(f"Yay bot has started! Named {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "otra vez" in message.content.lower():
        await message.channel.send(f"{message.author.mention} oop I was summoned")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def stat(ctx, *, args):
    team_number, *args = args.split()

    try:
        int(team_number)
    except ValueError:
        await ctx.reply("Invalid team number. Usage: ;stat [teamnum]")

    data = tba_client.team("frc" + team_number)

    if data.get("nickname", None) is None:
        await ctx.reply("No such team.")

    await ctx.reply(f"""
name: {data["nickname"]}
location: {data["city"]}, {data["state_prov"] and f"{data["state_prov"]}, "}{data["country"]}
school: {data["school_name"]}
rookie year: {data["rookie_year"]}
website: {data["website"]}""")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
