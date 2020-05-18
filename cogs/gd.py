from discord.ext import commands
import discord
import aiohttp
import asyncio
import gd
from .utils.paginator import Paginator
from .utils.http import get_page
import io

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
            level: gd.Level = levels[index]
            level_id = level.id
            name = level.name
            stars = level.stars
            if stars:
                name += f' ({stars}★)'
            description = level.description
            embed = discord.Embed(title=name, description=description, url=f'https://gdbrowser.com/{level_id}', color=0x87ff66)
            embed.set_thumbnail(url=self.level_icon(level))
            
            embed.add_field(name='Downloads', value=f"{level.downloads:,}")
            embed.add_field(name='Likes', value=f"{level.rating:,}")
            song = f'{level.song.name} - {level.song.author}'
            if level.song.is_custom():
                song = f'[{song}]({level.song.link})'
            embed.add_field(name='Song', value=song, inline=False)
            if level.creator.id != 0:
                url = ''
                if level.creator.is_registered():
                    url = f'https://gdbrowser.com/profile/{level.creator.name.replace(" ", "%20")}'
                embed.set_author(name=level.creator.name, url=url)
            
            embed.set_footer(text=f'ID: {level_id} | Level {index + 1}/{len(levels)}')
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
                'glow': int(icon.has_glow_outline())
            }
            params = '&'.join(f'{key}={str(value)}' for key, value in params.items())
            return f'https://gdbrowser.com/icon/a?{params}.png'
        else:
            return f'https://gdbrowser.com/icon/{user.name}'

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

            embed = discord.Embed(title=user.name, color=color, url=f'https://gdbrowser.com/profile/{user.name}')
            embed.add_field(name='Stars', value=f'{user.stars:,}{self.em_star}')
            embed.add_field(name='Demons', value=f'{user.demons:,}{self.em_demon}')
            embed.add_field(name='Coins', value=f'{user.coins:,}{self.em_coin}')
            embed.add_field(name='User Coins', value=f'{user.user_coins:,}{self.em_user_coin}')
            embed.add_field(name='Diamonds', value=f'{user.diamonds:,}💎')
            if user.cp:
                embed.add_field(name='Creator Points', value=f'{user.cp:,}{self.em_cp}')

            icon_url = self.user_icon(user)
            icon_data = await get_page(icon_url)
            icon_file = discord.File(io.BytesIO(icon_data), filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')

            try:
                comments = await user.get_page_comments(0)
            except gd.errors.NothingFound:
                pass
            else:
                embed.add_field(name='Latest comment', value=comments[0].body, inline=False)
            await ctx.send(file=icon_file, embed=embed)

def setup(bot):
    bot.add_cog(GD(bot))