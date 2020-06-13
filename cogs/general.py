import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import psutil
import os
import random
from .utils.time import format_time, format_date
from .utils.message import get_avatar, message_embed
from .utils.misc import run_command, mcserver_status
import time
import platform
import shutil
import json
import aiohttp
import pendulum
from cpuinfo import get_cpu_info
import io

class General(commands.Cog):
    __slots__ = 'bot', 'weather_key'
    def __init__(self, bot):
        self.bot = bot

        self.weather_key = self.bot.config['weather_key']

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

    def host_sync(self):
        if shutil.which('df') is None: return None
        cmd = run_command(('df', '/', '--output=used,size'))
        if cmd.ret: return None
        return tuple(map(int, cmd.out.decode('utf-8').splitlines()[1].split()))

    @commands.command(aliases=['hoststats', 'hostinfo', 'vps'])
    @commands.cooldown(1, 2, BucketType.default)
    async def host(self, ctx):
        """Sends some info about the bot's host"""
        embed = discord.Embed(title='Host information')

        brand = get_cpu_info().get('brand', 'Unknown')
        cpu = int(psutil.cpu_percent())
        cpu_bar = '█' * (cpu // 10) + ' ' * (10 - cpu // 10)
        cpu_bar = f'[{cpu_bar}]'
        embed.add_field(name='CPU', value=f'Name: {brand}\n Usage: {cpu}% `{cpu_bar}`', inline=False)
        
        gb = 1024 ** 3
        mem = psutil.virtual_memory()
        used = f'{mem.used / gb:.2f}'
        total = f'{mem.total / gb:.2f}'
        embed.add_field(name='RAM', value=f'{used}/{total} GB')

        data = await self.bot.loop.run_in_executor(None, self.host_sync)
        gb = 1024 ** 2
        if data is not None:
            embed.add_field(name='Disk', value=f'{data[0] / gb:.2f}/{data[1] / gb:.2f} GB')

        await ctx.send(embed=embed)

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

    @commands.command()
    @commands.cooldown(1, 10, BucketType.default)
    async def mcserver(self, ctx, server_ip):
        """Shows info for a minecraft server"""
        async with ctx.typing():
            server = await self.bot.loop.run_in_executor(None, mcserver_status, server_ip)
            if server is None:
                return await ctx.send('Error while trying to connect')
        embed = discord.Embed(title=f'**{server_ip}** status *[{int(server.ping)}ms]*', description=server.desc, colour=discord.Colour(0x339c31))
        embed.add_field(name='Version', value=server.version or 'Unknown')
        if len(server.players) == 0:
            players = 'Unknown' if server.online > 0 else 'No one'
        else:
            players = '\n'.join(f'- {player}' for player in server.players)
        embed.add_field(name=f'Players: {server.online}/{server.max}',
                        value=players)
        if server.icon:
            icon_file = discord.File(io.BytesIO(server.icon), filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
        await ctx.send(embed=embed, file=icon_file)

    @commands.command()
    @commands.cooldown(50, 60, BucketType.default)
    async def weather(self, ctx, *, city):
        """Shows weather info for given city"""
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.openweathermap.org/data/2.5/weather', params={
                    'appid': self.weather_key,
                    'q': city,
                    'units': 'metric'
                }) as r:
                    data = await r.json()
            # why didnt they just use code
            if data['cod'] != 200:
                return await ctx.send('Error: ' + data['message'])
            
            name = data['name'] + (f", {data['sys']['country']}" if 'country' in data['sys'] else '')

            weather = data['weather'][0]
            color = 0xedbc4b if weather['icon'][2] == 'd' else 0x0a0914
            
            embed = discord.Embed(title=name, url=f'https://openweathermap.org/city/{data["id"]}', colour=discord.Color(color))
            embed.description = weather['description'].capitalize()
            embed.set_thumbnail(url=f'http://openweathermap.org/img/wn/{weather["icon"]}@2x.png')

            temp = data['main']['temp']
            feel_temp = data['main']['feels_like']
            embed.add_field(name='Temperature', value=f"{temp:.0f}°C\n*Feels like {feel_temp:.0f}°C*", inline=False)

            date = pendulum.from_timestamp(data['dt'] + data['timezone'])
            embed.add_field(name='Date', value=f'{format_date(date)}', inline=False)

            humidity = data['main']['humidity']
            embed.add_field(name='Humidity', value=f'{humidity}%', inline=False)
            
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))