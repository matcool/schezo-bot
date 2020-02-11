import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import psutil
import os
import random
from .utils.time import format_time
from .utils.message import get_avatar, message_embed
from .utils.misc import run_command
import time
import platform
import shutil
import json
from mcstatus import MinecraftServer

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

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Sends the invite link for this bot"""
        await ctx.send(f'<https://discordapp.com/oauth2/authorize?client_id={ctx.bot.user.id}&scope=bot>')

    def speedtest_sync(self):
        if shutil.which('speedtest') is None: return None
        cmd = run_command(('speedtest', '--json'))
        return json.loads(cmd.out.decode('utf-8'))

    @commands.command()
    @commands.cooldown(1, 60, BucketType.default)
    async def speedtest(self, ctx: commands.Context):
        """Runs a speedtest on bot's host"""
        async with ctx.typing():
            data = await self.bot.loop.run_in_executor(None, self.speedtest_sync)
            if data is None:
                return await ctx.send('Speedtest is unavailable')
            download = data['download'] / 1000000
            upload = data['upload'] / 1000000
            ping = data['ping']
            await ctx.send(
                f'Ping: {ping:.1f}ms\n'
                f'Download: {download:.2f}Mbps\n'
                f'Upload: {upload:.2f}Mbps')

    def mcserver_sync(self, server_ip: str):
        server = MinecraftServer.lookup(server_ip)
        try:
            query = server.query(retries=1)
        except Exception:
            # Either query is disabled or failed to connect
            try:
                status = server.status(retries=1)
            except Exception:
                return False
            else:
                return (status.players.online, [p.name for p in status.players.sample or []], status.players.max, status.version.name)
        else:
            return (query.players.online, query.players.names, query.players.max, query.software.version)

    @commands.command()
    @commands.cooldown(1, 30, BucketType.default)
    async def mcserver(self, ctx, server_ip):
        """Shows info for a minecraft server"""
        result = await self.bot.loop.run_in_executor(None, self.mcserver_sync, server_ip)
        if not result:
            return await ctx.send('Error while trying to connect')
        online, players, max_players, version = result
        embed = discord.Embed(title=f'**{server_ip}** \'s status', colour=discord.Colour(0x339c31))
        embed.add_field(name='Version', value=version or 'Unknown')
        embed.add_field(name=f'Players: {online}/{max_players}', value='\n'.join(f'- {player}' for player in players) if len(players) > 0 else 'No one')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))