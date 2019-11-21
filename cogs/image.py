import discord
from discord.ext import commands

from .utils.message import get_nearest, get_avatar

from PIL import Image, ImageDraw, ImageFont
import io
import random
import math

# class name is Image_ as to not intefere with PIL's Image class
class Image_(commands.Cog, name='Image'):
    __slots__ = 'bot', 
    def __init__(self, bot):
        self.bot = bot

    def how_pil(self, image: bytes):
        how = Image.open('assets/how.jpg')
        image = Image.open(io.BytesIO(image))
        image = image.resize((544, 529), Image.ANTIALIAS).convert('RGB')
        how.paste(image, (88, 0))
        
        tmp = io.BytesIO()
        how.save(tmp, format='JPEG', quality=50)
        tmp.seek(0)
        return tmp

    @commands.command()
    async def how(self, ctx: commands.Context, *links):
        """
        HOW
        *command runs with image found in past 10 messages*
        """
        async with ctx.typing():
            # get_nearest defaults to nearest image
            image = await get_nearest(ctx)
            if image:
                img = await self.bot.loop.run_in_executor(None, self.how_pil, image)
                await ctx.send(file=discord.File(img, filename='HOW.jpeg'))
            else:
                await ctx.send('No image found')

    def networth_pil(self, pfp: bytes, name: str, user_id: int):
        networth = Image.new('RGBA', (1200, 421), color='WHITE')
        pfp = Image.open(io.BytesIO(pfp))
        pfp = pfp.resize((276, 276), Image.ANTIALIAS)
        networth.paste(pfp, (907, 95))

        draw = ImageDraw.Draw(networth)
        arial = ImageFont.truetype('arial.ttf', 35)

        text_w, _ = arial.getsize(name)

        draw.text((19, 21), name, font=arial, fill=(100, 100, 100))
        draw.text((19 + text_w, 21), ' / Net worth', font=arial, fill=0)

        arial = ImageFont.truetype('arial.ttf', 61)
        rnd = random.Random(user_id)
        smooth = lambda x: x * x * (3 - 2 * x)
        money = round(smooth(rnd.random()) * 3000, 2)
        draw.text((33, 181), f'${money:,}', font=arial, fill=0)

        draw.line((0, 76, networth.width, 76), fill=(230, 230, 230), width=2)
        
        tmp = io.BytesIO()
        networth.save(tmp, format='PNG')
        tmp.seek(0)
        return tmp

    @commands.command()
    async def networth(self, ctx: commands.Context, user: discord.Member=None):
        """Shows net worth for given user"""
        user = user or ctx.author
        async with ctx.typing():
            img = await self.bot.loop.run_in_executor(None, self.networth_pil, await get_avatar(user), user.name, user.id)
            await ctx.send(file=discord.File(img, filename='networth.png'))

def setup(bot):
    bot.add_cog(Image_(bot))