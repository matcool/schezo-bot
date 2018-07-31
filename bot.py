import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import json
import asyncio
import aiohttp
import datetime
import calendar
import re
#from os import listdir
import glob

#config file :P
with open('bot_config.json') as file:
    jsonf = json.load(file)
    gamename = jsonf['game']
    ownerid = jsonf['ownerid']
    desc = jsonf['desc']
    prefix = jsonf['prefix']
    token = jsonf['token']
    
bot = commands.Bot(command_prefix=prefix, description=desc, owner_id=int(ownerid), pm_help=None)

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
    #gamename = gamename_.replace('%numberofservers%', str(len(bot.guilds)))
    #print(bot.guilds)
    game = discord.Activity(name=gamename,type=discord.ActivityType.watching)
    await bot.change_presence(activity=game)
    loadCogs()

##@bot.event
##async def on_message(message):
##
##    #reply to dm with same
##    if not message.content.startswith("mb!") and type(message.channel) == discord.DMChannel and message.author.id != bot.user.id:
##        await message.channel.send('same')
##        return
##
##    #react nekro with gey
##    #if message.author.id == 168770585306857472 and random.randint(1,13) == 1:
##    #    await message.add_reaction(bot.get_emoji(287402139217559552))
##        
##    await bot.process_commands(message)
      
#--my commands

@bot.command(hidden=True,aliases=['rc'])
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
    await ctx.send(str(int(bot.latency*10000))+"ms")

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
async def serverpic(ctx,*,Id=None):
    """Sends pic of server icon"""
    if not ctx.guild and not Id: return
    if Id == None: g = ctx.guild
    else: g = bot.get_guild(int(Id))
    url = g.icon_url_as(format='png')
    await ctx.send(url)

@bot.command()
async def mock(ctx,*,msg=None):
    """dOeS thIS To yOuR meSsaGE"""
    if not msg:
        return
    await ctx.send("wOw mEsSaGE :\n"+"".join(list(map(lambda x: x if random.random() < 0.5 else x.upper(),msg.lower()))))

@bot.command()
async def scramble(ctx,*,msg=None):
    """Scramble the given word"""
    if not msg:
        return
    await ctx.send("Scrambled message :\n"+"".join(sorted(list(msg),key = lambda x: random.random())))

@bot.command()
async def createdat(ctx):
    """Says when you created your discord account"""
    a = ctx.message.author.created_at
    await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))



bot.run(token)