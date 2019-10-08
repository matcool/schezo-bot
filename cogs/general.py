import discord
from discord.ext import commands
import psutil
import os
import random
from .utils.time import format_time
from .utils.message import get_avatar

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """Sends some info about the bot"""
        process = psutil.Process(os.getpid())

        embed = discord.Embed(title='Schezo', description=f'''
        [Source code](https://github.com/matcool/schezo-bot)
        Memory usage: **{process.memory_info().rss/1024/1024:.2f}MB**''', colour=0x264a78)

        embed.set_thumbnail(url=await get_avatar(self.bot.user, url=True))

        embed.add_field(name='Uptime', value=format_time(int(self.bot.uptime)))
        embed.add_field(name='Guilds', value=len(self.bot.guilds))
        embed.add_field(name='Users', value=len(self.bot.users))
        embed.add_field(name='Cached Messages', value=len(self.bot.cached_messages))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))