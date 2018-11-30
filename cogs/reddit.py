from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import aiohttp
import random

class Reddit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(20,60,BucketType.default)
    async def eyebleach(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.reddit.com/r/eyebleach/hot.json') as r:
                js = await r.json()

        post = random.choice(js['data']['children'])['data']
        embed = discord.Embed(title=post['title'],url='https://reddit.com'+post['permalink'],color=0xa6edb0)
        embed.set_image(url=post['url'])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Reddit(bot))