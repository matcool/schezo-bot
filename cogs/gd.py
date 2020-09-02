from discord.ext import commands, tasks
import discord
import aiohttp
import asyncio
import gd
from .utils.paginator import Paginator
from .utils.http import get_page
import io

class GDEvents:
    def __init__(self, client: gd.Client, delay: float=1.5, pages: int=2, timely_delay: float=5):
        self.client = client
        self.delay = delay
        self.pages = pages
        self.timely_delay = timely_delay

        self.rated_cache = set()
        self.last_daily = None
        self.last_weekly = None

        self.listeners = {
            'rated': [],
            'daily': [],
            'weekly': []
        }

        self.rated_task = tasks.loop(minutes=self.delay)(self.fetch_rated)
        self.timely_task = tasks.loop(minutes=self.timely_delay)(self.fetch_timely)

    def add_listener(self, kind, listener):
        assert kind in {'rated', 'daily', 'weekly'}
        self.listeners[kind].append(listener)

    def start(self):
        self.rated_task.start()
        self.timely_task.start()

    def stop(self):
        if self.rated_task: self.rated_task.cancel()
        if self.timely_task: self.timely_task.cancel()

    async def fetch_rated(self):
        now_rated = await self.client.search_levels(filters=gd.Filters(strategy=gd.SearchStrategy.AWARDED), pages=range(self.pages))
        if self.rated_cache:
            levels = [i.id for i in now_rated if i.id not in self.rated_cache]
            if levels:
                await asyncio.sleep(5) # sometimes levels get rated and then featured, which is why the 5 second delay
                levels = await self.client.get_many_levels(*levels)
                for listener in self.listeners['rated']:
                    await listener(levels)
        self.rated_cache = {i.id for i in now_rated}
    
    async def fetch_timely(self):
        await self.fetch_daily()
        await self.fetch_weekly()

    async def fetch_daily(self):
        try:
            daily = await self.client.get_daily()
        except gd.MissingAccess:
            # level is most likely being updated, ignore
            return
        if self.last_daily and daily.id != self.last_daily:
            for listener in self.listeners['daily']:
                await listener(daily)
        self.last_daily = daily.id

    async def fetch_weekly(self):
        try:
            weekly = await self.client.get_weekly()
        except gd.MissingAccess:
            # level is most likely being updated, ignore
            return
        if self.last_weekly and weekly.id != self.last_weekly:
            for listener in self.listeners['weekly']:
                await listener(weekly)
        self.last_weekly = weekly.id

class GD(commands.Cog):
    __slots__ = ('bot', 'overwrite_name')

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.overwrite_name = 'Games'
        self.client = gd.Client()
    
        # hardcoded emotes lets go
        self.em_star = '<:gd_star:710548947965575238>'
        self.em_demon = '<:gd_demon:710549050444873809>'
        self.em_coin = '<:gd_coin:710548974691418183>'
        self.em_user_coin = '<:gd_user_coin:710549002784866335>'
        self.em_cp = '<:gd_cp:710549072053928029>'

        self.events = GDEvents(self.client)
        
        self.events.add_listener('rated', self.on_rated)
        self.events.add_listener('daily', self.on_daily)
        self.events.add_listener('weekly', self.on_weekly)
        
        self.events.start()

    def cog_unload(self):
        self.events.stop()

    def level_embed(self, level: gd.Level, color=0x87ff66) -> discord.Embed:
        level_id = level.id
        name = level.name
        stars = level.stars
        if stars:
            name += f' ({stars}★)'
        description = level.description
        embed = discord.Embed(title=name, description=description, url=f'https://gdbrowser.com/{level_id}', color=color)
        embed.set_thumbnail(url=self.level_icon(level))
        
        embed.add_field(name='Downloads', value=f"{level.downloads:,}")
        embed.add_field(name='Likes', value=f"{level.rating:,}")
        embed.add_field(name='Length', value=('Tiny', 'Short', 'Medium', 'Long', 'XL', 'Unknown')[level.length.value])
        song = level.song.name
        if level.song.is_custom():
            song = f'[{song}]({level.song.link})'
        embed.add_field(name='Song', value=song, inline=False)
        if level.creator.id != 0:
            url = ''
            if level.creator.is_registered():
                url = f'https://gdbrowser.com/profile/{level.creator.name.replace(" ", "%20")}'
            embed.set_author(name=level.creator.name, url=url)
        
        embed.set_footer(text=f'ID: {level_id}')
        return embed

    async def rated_channels(self):
        return [i['gd_updates'] async for i in self.bot.gf.db.find({'gd_updates': {'$not': {'$eq': None}}}, {'gd_updates': True})]

    async def on_rated(self, levels):
        embeds = [self.level_embed(level, color=0xfffd00) for level in levels]
        for channel in await self.rated_channels():
            channel = self.bot.get_channel(channel)
            for embed in embeds:
                await channel.send('New rated level!', embed=embed)

    async def on_daily(self, level):
        embed = self.level_embed(level, color=0xf72c2c)
        for channel in await self.rated_channels():
            channel = self.bot.get_channel(channel)
            await channel.send('New daily!', embed=embed)

    async def on_weekly(self, level):
        embed = self.level_embed(level, color=0x555555)
        for channel in await self.rated_channels():
            channel = self.bot.get_channel(channel)
            await channel.send('New weekly!', embed=embed)

    @commands.group(name='gd')
    async def gd_(self, ctx):
        """
        Group of Geometry Dash related commands.
        Examples::
        > search yeah
        the level
        > search 123456
        the exact level
        """
        return

    @staticmethod
    def level_icon(level: gd.Level) -> str:
        if not level.is_demon():
            name = ''
            if level.difficulty == gd.LevelDifficulty.NA:
                name = 'unrated'
            elif level.difficulty == gd.LevelDifficulty.AUTO:
                name = 'auto'
            else:
                name = level.difficulty.name.lower()
        else:
            name = 'demon-' + ('easy', 'medium', 'hard', 'insane', 'extreme')[level.difficulty.value - 1]
        if level.is_epic():
            name += '-epic'
        elif level.is_featured():
            name += '-featured'
        return f'https://gdbrowser.com/difficulty/{name}.png'

    @gd_.command()
    async def level(self, ctx, *, query):
        levels = await self.client.search_levels(query, pages=range(2))
        if len(levels) == 0:
            return await ctx.send('No level found')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in '◀️▶'

        def get_embed(index) -> discord.Embed:
            level = levels[index]
            embed = self.level_embed(level)
            embed.set_footer(text=f'ID: {level.id} | Level {index + 1}/{len(levels)}')
            return embed

        if len(levels) == 1:
            return await ctx.send(embed=get_embed(0))

        paginator = Paginator(len(levels), get_embed)
        await paginator.start(ctx)

    @staticmethod
    def user_icon(user: gd.User) -> str:
        if True:
            icon = user.icon_set
            params = {
                'noUser': 1,
                'icon': icon.cube,
                'col1': icon.color_1.index,
                'col2': icon.color_2.index,
                'glow': icon.has_glow_outline()
            }
            params = '&'.join(f'{key}={str(value)}' for key, value in params.items() if value)
            return f'https://gdbrowser.com/icon/a?{params}'
        else:
            return f'https://gdbrowser.com/icon/{user.name.replace(" ", "%20")}'

    @gd_.command()
    async def user(self, ctx, *, query):
        async with ctx.typing():
            try:
                user: gd.User = await self.client.search_user(query)
            except gd.MissingAccess:
                return await ctx.send('No user found')
            if not user.is_registered():
                return await ctx.send('User not registered')

            color = user.icon_set.color_1.value
            if color == 0xffffff:
                color = 0xfffffe # thank you discord

            embed = discord.Embed(title=user.name, color=color, url=f'https://gdbrowser.com/profile/{user.name.replace(" ", "%20")}')
            embed.add_field(name='Stars', value=f'{user.stars:,}{self.em_star}')
            embed.add_field(name='Demons', value=f'{user.demons:,}{self.em_demon}')
            embed.add_field(name='Coins', value=f'{user.coins:,}{self.em_coin}')
            embed.add_field(name='User Coins', value=f'{user.user_coins:,}{self.em_user_coin}')
            embed.add_field(name='Diamonds', value=f'{user.diamonds:,}💎')
            if user.cp:
                embed.add_field(name='Creator Points', value=f'{user.cp:,}{self.em_cp}')

            icons_data = await get_page(f'http://nekit.xyz/api/icons/all/{user.name}'.replace(' ', '%20'))
            icons_file = discord.File(io.BytesIO(icons_data), filename='icons.png')
            embed.set_image(url='attachment://icons.png')

            comments = await user.get_page_comments(0)
            if comments:
                embed.add_field(name='Latest comment', value=comments[0].body, inline=False)
            await ctx.send(file=icons_file, embed=embed)

    @gd_.command()
    async def daily(self, ctx):
        try:
            level = await self.client.get_daily()
        except gd.MissingAccess:
            return await ctx.send('Could not fetch daily')
        
        await ctx.send(embed=self.level_embed(level, color=0xf72c2c))

    @gd_.command()
    async def weekly(self, ctx):
        try:
            level = await self.client.get_weekly()
        except gd.MissingAccess:
            return await ctx.send('Could not fetch weekly')
        
        await ctx.send(embed=self.level_embed(level, color=0x555555))


def setup(bot):
    bot.add_cog(GD(bot))