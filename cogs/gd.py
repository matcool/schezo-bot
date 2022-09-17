from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
import discord
import aiohttp
import asyncio
import gd
from gd import SearchStrategy
from .utils.paginator import Paginator
from .utils.http import get_page
from .utils.misc import parse_args
import io
import re

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
        now_rated = await self.client.search_levels(filters=gd.Filters(strategy=SearchStrategy.AWARDED), pages=range(self.pages))
        # If the list is empty gd servers are most likely dead
        if not now_rated: return
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
        self.em_mod = '<:gd_mod:763864307065683978>'
        self.em_mod_elder = '<:gd_mod_elder:763864329036103722>'

        self.events = GDEvents(self.client)
        
        self.events.add_listener('rated', self.on_rated)
        self.events.add_listener('daily', self.on_daily)
        self.events.add_listener('weekly', self.on_weekly)
        
        # self.events.start()

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
            song = f'[{song}]({level.song.url})'
        embed.add_field(name='Song', value=song, inline=False)
        if level.creator.id != 0:
            url = ''
            if level.creator.id and level.creator.account_id:
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
        > level yeah
        the level
        > level 123456
        the exact level
        """
        return

    @staticmethod
    def level_icon(level: gd.Level) -> str:
        # print(f'diff is {level.difficulty}')
        return f'https://gdbrowser.com/assets/difficulties/unrated.png'
        if level.difficulty != level.difficulty.DEMON:
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
        return f'https://gdbrowser.com/assets/difficulties/{name}.png'

    @gd_.command()
    async def level(self, ctx, *, query):
        """
        Search levels.

        List of all args:
        `--user [username]`
        `--difficulty [difficulties separated by spaces]`
        `--length [lengths separated by spaces]`
        `--song [official song name]`
        `--song-id [newgrounds song id]`
        `--coins`
        `--featured`
        `--epic`
        `--rated`
        `--no-star`
        `--original`
        `--2-player`
        `--downloads`
        `--likes`
        `--recent`
        `--magic`
        `--trending`
        `--hall-of-fame`
        `--awarded`

        Examples::
        > level easy
        Looks up level easy
        > --user mat4
        Looks up all levels by `mat4`
        > challenge --length tiny short
        Looks up challenge levels that are tiny or short
        > --length tiny short --rated
        Looks up all rated level that are tiny or short
        > --difficulty extreme_demon --song-id 467339
        Looks up all extreme demons with the most original song
        """
        if not query.isnumeric():
            # maybe change to / ?
            query, args = parse_args(query, arg_prefix='--')

            async def invalid_value(arg, msg):
                await ctx.send(f'Invalid value on argument `{arg}`: {msg}')

            search_filter = {}
            user = None
            for key, value in args.items():
                if value:
                    value = value.strip()
                if key == 'difficulty' or key == 'diff':
                    if not value:
                        return await invalid_value(key, 'Difficulty value is empty')
                    value = value.lower()
                    diffs = value.split(' ')
                    diff_names = {'na', 'easy', 'normal', 'hard', 'harder', 'insane', 'demon'}
                    demon_names = {'easy_demon', 'medium_demon', 'hard_demon', 'insane_demon', 'extreme_demon'}
                    if '_demon' in value:
                        if len(diffs) > 1:
                            return await invalid_value(key, 'Only one demon difficulty is allowed')
                        diff = diffs[0]
                        if diff not in demon_names:
                            return await invalid_value(key, 'Invalid difficulty')
                        search_filter['difficulties'] = [gd.Difficulty.from_name(diff)]
                    else:
                        for diff in diffs:
                            if diff not in diff_names:
                                return await invalid_value(key, 'Invalid difficulty')
                        search_filter['difficulties'] = [gd.Difficulty.from_name(d) for d in diffs]
                elif key == 'length':
                    if not value:
                        return await invalid_value(key, 'Length value is empty')
                    names = ['tiny', 'short', 'medium', 'long', 'xl', 'extra_long']
                    lengths = value.lower().split(' ')
                    for length in lengths:
                        if length not in names:
                            return await invalid_value(key, 'Invalid length')
                    search_filter['lengths'] = [gd.LevelLength.from_value(min(names.index(name), 4)) for name in lengths]
                elif key == 'song':
                    if not value:
                        return await invalid_value(key, 'Song value is empty')
                    songs = ['stereo madness', 'back on track', 'polargeist', 'dry out',
                    'base after base', 'cant let go', 'jumper', 'time machine',
                    'cycles', 'xstep', 'clutterfunk', 'theory of everything', 'electroman adventures',
                    'clubstep', 'electrodynamix', 'hexagon force', 'blast processing', 'theory of everything 2',
                    'geometrical dominator', 'deadlocked', 'fingerdash']
                    try:
                        search_filter['song_id'] = songs.index(value.lower()) + 1
                    except ValueError:
                        return await invalid_value(key, 'Invalid song')
                elif key == 'song-id' or key == 'custom-song':
                    if not value:
                        return await invalid_value(key, 'Song ID is empty')
                    try:
                        song_id = int(value)
                    except ValueError:
                        return await invalid_value(key, 'Invalid song ID')
                    search_filter['song_id'] = song_id
                    search_filter['custom_song'] = True
                elif key == 'creator' or key == 'user':
                    if not value:
                        return await invalid_value(key, 'Value is empty')
                    try:
                        user = await self.client.search_user(value.replace('"', ''), simple=True)
                    except gd.MissingAccess:
                        return await invalid_value(key, 'User not found')
                    search_filter['strategy'] = SearchStrategy.BY_USER
                elif key == 'coins':
                    search_filter['require_coins'] = True
                elif key == 'featured':
                    search_filter['featured'] = True
                elif key == 'epic':
                    search_filter['epic'] = True
                elif key == 'rated' or key == 'star':
                    search_filter['rated'] = True
                elif key == 'no-star':
                    search_filter['rated'] = False
                elif key == '2-player' or key == '2player' or key == 'two-player' or key == 'twoplayer':
                    search_filter['require_two_player'] = True
                elif key == 'original':
                    search_filter['require_original'] = True
                elif key == 'most-downloaded' or key == 'downloads':
                    search_filter['strategy'] = SearchStrategy.MOST_DOWNLOADED
                elif key == 'most-liked' or key == 'most-likes' or key == 'likes':
                    search_filter['strategy'] = SearchStrategy.MOST_LIKED
                elif key == 'trending':
                    search_filter['strategy'] = SearchStrategy.TRENDING
                elif key == 'recent':
                    search_filter['strategy'] = SearchStrategy.RECENT
                elif key == 'magic':
                    search_filter['strategy'] = SearchStrategy.MAGIC
                elif key == 'awarded':
                    search_filter['strategy'] = SearchStrategy.AWARDED
                elif key == 'hall-of-fame' or key == 'hof':
                    search_filter['strategy'] = SearchStrategy.HALL_OF_FAME

            gd_filter = gd.Filters(**search_filter)

            levels = await self.client.search_levels(query, pages=range(2), filters=gd_filter, user=user)
        else:
            try:
                levels = [await self.client.get_level(int(query), get_data=False)]
            except Exception:
                levels = []

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
            except (gd.MissingAccess, gd.DeError):
                return await ctx.send('No user found')
            if not (user.account_id and user.id):
                return await ctx.send('User not registered')

            color = user.color_1.value
            if color == 0xffffff:
                color = 0xfffffe # thank you discord

            embed = discord.Embed(title=user.name, color=color, url=f'https://gdbrowser.com/profile/{user.name.replace(" ", "%20")}')
            embed.add_field(name='Stars', value=f'{user.stars:,}{self.em_star}')
            embed.add_field(name='Demons', value=f'{user.demons:,}{self.em_demon}')
            embed.add_field(name='Coins', value=f'{user.coins:,}{self.em_coin}')
            embed.add_field(name='User Coins', value=f'{user.user_coins:,}{self.em_user_coin}')
            embed.add_field(name='Diamonds', value=f'{user.diamonds:,}💎')
            if user.creator_points:
                embed.add_field(name='Creator Points', value=f'{user.creator_points:,}{self.em_cp}')

            # try:
            #     icons_data = await get_page(f'http://nekit.dev/api/icons/all/{user.name}'.replace(' ', '%20'))
            #     icons_file = discord.File(io.BytesIO(icons_data), filename='icons.png')
            #     embed.set_image(url='attachment://icons.png')
            # except Exception:
            #     # nekit's website is most likely down, ignore
            #     icons_file = None

            embed.set_footer(text=f'Account ID: {user.account_id}')

            if user.role == user.role.MODERATOR or user.role == user.role.ELDER_MODERATOR:
                embed.title = f'{self.em_mod_elder if user.role == user.role.ELDER_MODERATOR else self.em_mod} {embed.title}'

            comments = await user.get_comments_on_page(0)
            if comments:
                embed.add_field(name='Latest comment', value=comments[0].content, inline=False)
            await ctx.send(embed=embed)

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

    @commands.cooldown(1, 5, BucketType.default)
    @gd_.command()
    async def song(self, ctx, song_id: int):
        """Gets info about a newgrounds song"""
        async with ctx.typing():
            emoji = lambda x: '\\✅' if x else '\\❌'
            try:
                info = await self.client.get_song(song_id)
            except (gd.SongRestricted, gd.MissingAccess):
                return await ctx.send('Song not found')
                # either the song doesn't actually exist or
                # the artist isn't scouted
                # (maybe even external api disabled? idk)
                # try:
                #     info = await self.client.get_newgrounds_song(song_id)
                # except gd.MissingAccess:
            song = {
                'name': info.name,
                'url': f'https://www.newgrounds.com/audio/listen/{song_id}',
                'artist': info.artist.name,
                'artist_url': info.artist.url,
                # 'scouted': info.is_scouted(),
                # 'whitelisted': info.is_whitelisted()
            }
            await ctx.send(embed=discord.Embed(title=song['name'], url=song['url'], color=0xd4d5d6,
                description=f'*by [{song["artist"]}]({song["artist_url"]})*\n\n'
                # f'{emoji(song["scouted"])} Scouted\n'
                # f'{emoji(song["whitelisted"])} Allowed in GD'
            ).set_thumbnail(url=f'https://aicon.ngfiles.com/{str(song_id)[:3]}/{song_id}.png'))


async def setup(bot):
    await bot.add_cog(GD(bot))