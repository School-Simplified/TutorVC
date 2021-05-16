import asyncio
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
import aiohttp
import discord
from discord.ext import commands
import chat_exporter

#Applying towards intents
intents = discord.Intents.default()  
intents.reactions = True
intents.members = True
intents.presences = True
intents.voice_states = True

#Defining client and SlashCommands
client = commands.Bot(command_prefix="+", intents=intents, case_insensitive = True)
client.remove_command('help')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_extensions():  # Gets extension list dynamically
    extensions = []
    for file in Path("cogs").glob("**/*.py"):
        if "!" in file.name or "__" in file.name:
            continue
        extensions.append(str(file).replace("/", ".").replace(".py", ""))
    return extensions

async def force_restart(ctx):  #Forces REPL to apply changes to everything
    try:
        subprocess.run("python main.py", shell=True, text=True, capture_output=True, check=True)
    except Exception as e:
        await ctx.send(f"❌ Something went wrong while trying to restart the bot!\nThere might have been a bug which could have caused this!\n**Error:**\n{e}")
    finally:
        sys.exit(0)


 
@client.event
async def on_ready():
    print(discord.__version__)
    now = datetime.now()
    print("Current Time =", now)
    print(f"{bcolors.WARNING}Loading audio files...{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}masaAudio.mp3 - 100% | Status: LOADED{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}startCH.mp3 - 100% | Status: LOADED{bcolors.ENDC}")

    print(f"{bcolors.OKBLUE}CONNECTED TO DISCORD{bcolors.ENDC}")
    chat_exporter.init_exporter(client)
    guild = await client.fetch_guild(783914689847361537)
    #botVoiceState = guild.get_member(842468709406081034)

    voice = discord.utils.get(client.voice_clients, guild=guild)

    if voice == None:
        voiceChannel = await client.fetch_channel(842587545070206976)

        global vc
        vc = await voiceChannel.connect()
    else:
        pass



for ext in get_extensions():
    client.load_extension(ext)


@client.group(aliases=['cog'])
@commands.is_owner()
async def cogs(ctx):
    pass


@cogs.command()
@commands.is_owner()
async def unload(ctx, ext):
    if "cogs." not in ext:
        ext = f"cogs.{ext}"
    if ext in get_extensions():
        client.unload_extension(ext)
        embed = discord.Embed(
            title="Cogs - Unload", description=f"Unloaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Cogs Reloaded", description=f"Cog '{ext}' not found", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command()
@commands.is_owner()
async def load(ctx, ext):
    if "cogs." not in ext:
        ext = f"cogs.{ext}"
    if ext in get_extensions():
        client.load_extension(ext)
        embed = discord.Embed(title="Cogs - Load",
                              description=f"Loaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Cogs - Load", description=f"Cog '{ext}' not found.", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command(aliases=['restart'])
@commands.is_owner()
async def reload(ctx, ext):
    if ext == "all":
        embed = discord.Embed(
            title="Cogs - Reload", description="Reloaded all cogs", color=0xd6b4e8)
        for extension in get_extensions():
            client.reload_extension(extension)
        await ctx.send(embed=embed)
        return

    if "cogs." not in ext:
        ext = f"cogs.{ext}"

    if ext in get_extensions():
        client.reload_extension(ext)
        embed = discord.Embed(
            title="Cogs - Reload", description=f"Reloaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Cogs - Reload", description=f"Cog '{ext}' not found.", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command()
@commands.is_owner()
async def view(ctx):
    msg = " ".join(get_extensions())
    embed = discord.Embed(title="Cogs - View", description=msg, color=0xd6b4e8)
    await ctx.send(embed=embed)


@client.command()
async def ping(ctx):
    pingembed = discord.Embed(title="Pong! ⌛", color=0xb10d9f, description="Current Discord API Latency")
    pingembed.add_field(name="Current Ping:",value=f'{round(client.latency * 1000)}ms')
    await ctx.send(embed=pingembed)


client.run("token")


