import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import psutil
import os
import random
from .utils.time import format_time
from .utils.message import get_avatar, message_embed
import time
import platform

class General(commands.Cog):
    __slots__ = 'bot', 
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """Sends some info about the bot"""
        process = psutil.Process(os.getpid())

        embed = discord.Embed(title='Schezo', description=f'[Source code](https://github.com/matcool/schezo-bot)', colour=0x264a78)

        embed.set_thumbnail(url=await get_avatar(self.bot.user, url=True))

        embed.add_field(name='Uptime', value=format_time(int(self.bot.uptime)))
        embed.add_field(name='Memory usage', value=f'{process.memory_info().rss/1024/1024:.2f}MB')
        embed.add_field(name='Guilds', value=len(self.bot.guilds))
        embed.add_field(name='Users', value=len(self.bot.users))
        
        embed.set_footer(text=f'Running on {platform.python_implementation()} {platform.python_version()} with discord.py {discord.__version__}')

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 2, BucketType.default)
    async def ping(self, ctx):
        """Sends bot's latency"""
        start = time.time()
        msg = await ctx.send(f'Websocket: {int(self.bot.latency*1000)}ms')
        end = time.time()
        await msg.edit(content=f'Websocket: {int(self.bot.latency*1000)}ms\n'
                               f'Message: {int((end-start)*1000)}ms')

    @commands.command(aliases=['hoststats', 'hostinfo', 'vps'])
    async def host(self, ctx):
        """Sends some info about the bot's host"""
        gb = 1024 ** 3
        cpu = int(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        used = f'{mem.used / gb:.2f}'
        total = f'{mem.total / gb:.2f}'
        await ctx.send(f'CPU Usage: {cpu}%\n'
                       f'RAM Usage: {used}GiB/{total}GiB')

    @commands.command(alises=['reply'])
    async def quote(self, ctx, msg: discord.Message):
        """Sends given message in an embed
        Useful for quoting and earlier message
        Works with message link (recommended) or message id (not so reliable)"""
        embed = await message_embed(msg)
        await ctx.send(embed=embed)
        if ctx.guild and ctx.guild.me.permissions_in(ctx.channel).manage_messages:
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(General(bot))