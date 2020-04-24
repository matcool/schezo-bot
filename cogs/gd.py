from discord.ext import commands
import discord
import aiohttp
import asyncio

class GD(commands.Cog, name='Geometry Dash'):
    __slots__ = ('bot')

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group()
    async def gd(self, ctx):
        """
        Group of Geometry Dash related commands.
        <examples>
        <cmd>search yeah</cmd>
        <res>the level</res>
        <cmd>search 123456</cmd>
        <res>the exact level</res>
        </examples>
        """
        return

    @gd.command()
    async def search(self, ctx, *, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://gdbrowser.com/api/search/{query}') as r:
                if await r.text() == '-1':
                    return await ctx.send('No level found')
                data = await r.json()

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in '◀️▶'

        def get_embed(index) -> discord.Embed:
            level = data[index]
            level_id = level['id']
            name = level['name']
            stars = int(level['stars'])
            if stars:
                name += f' ({stars}★)'
            description = level['description']
            embed = discord.Embed(title=name, description=description, url=f'https://gdbrowser.com/{level_id}', color=0x87ff66)
            embed.set_thumbnail(url=f'https://gdbrowser.com/difficulty/{level["difficultyFace"]}.png')
            
            embed.add_field(name='Downloads', value=f"{int(level['downloads']):,}")
            embed.add_field(name='Likes', value=f"{int(level['likes']):,}")
            song = f'{level["songName"]} - {level["songAuthor"]}'
            embed.add_field(name='Song', value=song, inline=False)
            if level['author'] != '-':
                url = ''
                if int(level['accountID']):
                    url = f'https://gdbrowser.com/profile/{level["author"].replace(" ", "%20")}'
                embed.set_author(name=level['author'], url=url)
            
            embed.set_footer(text=f'ID: {level_id} | Level {index + 1}/{len(data)}')
            return embed

        message = await ctx.send(embed=get_embed(0))
        if len(data) == 1: return

        await message.add_reaction('◀️')
        await message.add_reaction('▶')

        index = 0
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                break
            else:
                edit = True
                if str(reaction.emoji) == '▶':
                    edit = index != len(data) - 1
                    index = min(index + 1, len(data) - 1)
                else:
                    edit = index != 0
                    index = max(index - 1, 0)
                if edit: await message.edit(embed=get_embed(index))
                try:
                    await reaction.remove(user)
                except Exception:
                    continue
        

def setup(bot):
    bot.add_cog(GD(bot))