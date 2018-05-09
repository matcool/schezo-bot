import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import json
import asyncio
import aiohttp
import datetime
import sys
import calendar
import re
from os import listdir


#modules
sys.path.insert(0, "../modules")

import MatStuff

sys.path.pop(0)

#config file :P
with open('bot_config.json') as file:
    jsonf = json.load(file)
    gamename = jsonf['game']
    ownerid = jsonf['ownerid']
    desc = jsonf['desc']
    prefix = jsonf['prefix']
    token = jsonf['token']
    
bot = commands.Bot(command_prefix=prefix, description=desc, owner_id=int(ownerid), pm_help=None)

#useless variables

allemojis = bot.emojis


def loadCogs():
    for i in listdir('cogs'):
        if i[-2:] == 'py':
            bot.load_extension('cogs.'+i[:-3])

def unloadCogs():
    for i in listdir('cogs'):
        if i[-2:] == 'py':
            bot.unload_extension('cogs.'+i[:-3])


#events
@bot.event
async def on_ready():
    print('Logged in ass')
    print(bot.user.name)
    print(bot.user.id)
    gamename2 = gamename.replace('%numberofservers%', str(len(bot.guilds)))
    game = discord.Game(gamename2)
    await bot.change_presence(activity=game)
    loadCogs()

@bot.event
async def on_message(message):

    #reply to dm with same
    if not message.content.startswith("mb!") and type(message.channel) == discord.DMChannel and message.author.id != bot.user.id:
        await message.channel.send('same')
        return

    #react nekro with gey
    if message.author.id == 168770585306857472 and random.randint(1,13) == 1:
        await message.add_reaction(bot.get_emoji(287402139217559552))
        
    await bot.process_commands(message)
      
#--my commands

@bot.command(hidden=True)
@commands.is_owner()
async def reloadcogs(ctx):
    unloadCogs()
    loadCogs()
    await ctx.send("done")


#--every1 commands
@bot.command()
async def embed(ctx,title,content,color):
    """Makes a embed message with the args given."""
    embed = discord.Embed(title=title, description=content, colour=int(color, 16))
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Tests the bot latency"""
    await ctx.send(str(int(bot.latency*1000))+" seconds")

@bot.command()
async def spacefy(ctx,*, string: str):
    """a e s t h e t i c 'fy the given string."""
    await ctx.send(" ".join(string))

@bot.command()
async def invite(ctx):
    """Sends this bot invite link."""
    part1 = 'https://discordapp.com/oauth2/authorize?'
    part2 = 'client_id=317323392992935946&scope=bot&permissions=270400'
    await ctx.send(part1+part2)

@bot.command()
async def joinedat(ctx):
    """Says when you joined the server"""
    a = ctx.message.author.joined_at
    await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))

@bot.command()
async def pfp(ctx,uid=None):
    """Gets a profile pic from id or from msg author"""
    if uid is None:
        await ctx.send(ctx.message.author.avatar_url_as(format="png"))
    else:
        m = bot.get_user(int(uid))
        await ctx.send(m.avatar_url_as(format="png"))

@bot.command()
async def serverpic(ctx):
    """Sends pic of server icon"""
    await ctx.send(ctx.message.guild.icon_url)

@bot.command()
async def mock(ctx,*,msg="ok guys"):
    """dOeS thIS To yOuR meSsaGE"""
    await ctx.send("wOw mEsSaGE :\n"+MatStuff.uppLetters(msg))

@bot.command()
async def scramble(ctx,*,msg="ok guys"):
    """Scramble the given word"""
    await ctx.send("Scrambled message :\n"+MatStuff.scrambleW(msg))

@bot.command()
async def createdat(ctx):
    """Says when you created your discord account"""
    a = ctx.message.author.created_at
    await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))




bot.run(token)