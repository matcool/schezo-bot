import discord
from discord.ext import commands
import json
import glob
from hashlib import sha1
import aiohttp
import re
import asyncio

with open('bot_config.json') as file:
    jsonf = json.load(file)
    gamename = jsonf['game']
    ownerid = jsonf['ownerid']
    prefix = jsonf['prefix']
    token = jsonf['token']
    
bot = commands.Bot(command_prefix=prefix, owner_id=int(ownerid), pm_help=None)

#Custom help command is in cogs/custom_help
bot.remove_command("help")

def getCogs():
    for i in list(map(lambda p: p.replace('\\','.').replace('/','.')[:-3], glob.glob("cogs/*.py"))):
        yield i

def loadCogs():
    for i in getCogs():
        bot.load_extension(i)

def unloadCogs():
    extensions = bot.extensions.copy().keys()
    for i in extensions:
        bot.unload_extension(i)

async def uptime(bot):
    await bot.wait_until_ready()
    bot.uptime = 0 
    while not bot.is_closed():
        await asyncio.sleep(10)
        bot.uptime += 10

#events
@bot.event
async def on_ready():
    print('Logged in ass')
    print(bot.user.name)
    print(bot.user.id)
    game = discord.Activity(name=gamename,type=discord.ActivityType.watching)
    await bot.change_presence(activity=game)
    bot.loop.create_task(uptime(bot))
    loadCogs()

@bot.event
async def on_message(message):
    # something goes here
    await bot.process_commands(message)
      
#--my commands

@bot.command(hidden=True,aliases=['rc'])
@commands.is_owner()
async def reloadcogs(ctx):
    unloadCogs()
    loadCogs()
    await ctx.send("done")

bot.run(token)
