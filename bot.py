import discord
from discord.ext import commands
import json
import glob
from hashlib import sha1
import aiohttp

#config file :P
with open('bot_config.json') as file:
    jsonf = json.load(file)
    gamename = jsonf['game']
    ownerid = jsonf['ownerid']
    desc = jsonf['desc']
    prefix = jsonf['prefix']
    token = jsonf['token']
    
bot = commands.Bot(command_prefix=prefix, description=desc, owner_id=int(ownerid), pm_help=None)

#Custom help command is in cogs/miscellaneous
bot.remove_command("help")

def getCogs():
    for i in list(map(lambda p: p.replace('\\','.').replace('/','.')[:-3], glob.glob("cogs/*.py"))):
        yield i

def loadCogs():
    for i in getCogs():
        bot.load_extension(i)


def unloadCogs():
    for i in getCogs():
        bot.unload_extension(i)


#events
@bot.event
async def on_ready():
    print('Logged in ass')
    print(bot.user.name)
    print(bot.user.id)
    game = discord.Activity(name=gamename,type=discord.ActivityType.watching)
    await bot.change_presence(activity=game)
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
