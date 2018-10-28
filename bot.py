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
    if message.channel.id == 418209286905135107 and len(message.attachments) > 0:
        bad = '4758f1600d62c7363e789ad6902a62eb398823e0'
        async with aiohttp.ClientSession() as session:
            async with session.get(message.attachments[0].url) as response:
                result = await response.read()

        if sha1(result).hexdigest() == bad:
            await message.channel.send('ew :puke:')
    await bot.process_commands(message)

# @bot.event
# async def on_message(message):

    # #reply to dm with same
    # if not message.content.startswith("mb!") and type(message.channel) == discord.DMChannel and message.author.id != bot.user.id:
    #     await message.channel.send('same')
    #     return

    # #react nekro with gey
    # #if message.author.id == 168770585306857472 and random.randint(1,13) == 1:
    # #    await message.add_reaction(bot.get_emoji(287402139217559552))

    #await bot.process_commands(message)

@bot.event
async def on_command(ctx):
    print("mb!"+ctx.command.name)
      
#--my commands

@bot.command(hidden=True,aliases=['rc'])
@commands.is_owner()
async def reloadcogs(ctx):
    unloadCogs()
    loadCogs()
    await ctx.send("done")

bot.run(token)
