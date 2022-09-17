import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.message import get_nearest, get_avatar

from PIL import Image, ImageDraw, ImageFont, ImageChops
import io
import random
import math

def save_image(img, *args, **kwargs) -> io.BytesIO:
    tmp = io.BytesIO()
    img.save(tmp, *args, **kwargs)
    tmp.seek(0)
    return tmp

class Image_(commands.Cog, name='Image'):
    __slots__ = 'bot', 
    def __init__(self, bot):
        self.bot = bot

    async def basic_image_command(self, ctx: commands.Context, pil_func, *args, filename='image.png'):
        async with ctx.typing():
            # get_nearest defaults to nearest image
            image = await get_nearest(ctx)
            if image:
                img = await self.bot.loop.run_in_executor(None, pil_func, image, *args)
                await ctx.send(file=discord.File(img, filename=filename))
            else:
                await ctx.send('No image found')

    def how_pil(self, image: bytes):
        how = Image.open('assets/how.jpg')
        image = Image.open(io.BytesIO(image))
        image = image.resize((544, 529), Image.ANTIALIAS).convert('RGB')
        how.paste(image, (88, 0))
        
        return save_image(how, format='JPEG', quality=50)

    @commands.command()
    async def how(self, ctx: commands.Context, *links):
        """HOW"""
        return await self.basic_image_command(ctx, self.how_pil, filename='HOW.jpeg')

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

        return save_image(networth, format='PNG')

    @commands.command()
    async def networth(self, ctx: commands.Context, user: discord.Member=None):
        """Shows net worth for given user"""
        user = user or ctx.author
        async with ctx.typing():
            img = await self.bot.loop.run_in_executor(None, self.networth_pil, await get_avatar(user), user.name, user.id)
            await ctx.send(file=discord.File(img, filename='networth.png'))

    def google_pil(self, image: bytes):
        google = Image.open('assets/google.jpg')
        image = Image.open(io.BytesIO(image))
        image = image.resize((526, 309), Image.ANTIALIAS).convert('RGB')
        google.paste(image, (0, 425))
        
        return save_image(google, format='JPEG', quality=50)

    @commands.command()
    async def google(self, ctx: commands.Context, *links):
        """
        Google
        https://google.com
        """
        return await self.basic_image_command(ctx, self.google_pil, filename='google.jpeg')

    def byemom_pil(self, image: bytes):
        byemom = Image.open('assets/byemom.png')
        image = Image.open(io.BytesIO(image))
        image = image.resize((340, 180), Image.ANTIALIAS).convert('RGB')
        byemom.paste(image, (0, 0))
        
        return save_image(byemom, format='JPEG', quality=50)

    @commands.command()
    async def byemom(self, ctx: commands.Context, *links):
        """BYE MOM!!"""
        return await self.basic_image_command(ctx, self.byemom_pil, filename='BYEMOM!.jpeg')

    def reddit_pil(self, image: bytes, username: str):
        choice = random.choice(('wholesome', 'everyone', 'reddit', 'reddit-post', 'reddit-watermark', 'reddit-imin', 'reddit-killedher', 'reddit-tumblr', 'nobody'))

        if choice != 'nobody':
            overlay = Image.open(f'assets/{choice}.png')
        image = Image.open(io.BytesIO(image))
        final = None
        if choice == 'reddit-post':
            image = image.resize((542, 512), Image.ANTIALIAS).convert('RGBA')
            overlay.paste(image, (78, 72))
            final = overlay
        elif choice == 'reddit-watermark':
            overlay = overlay.resize((image.width // 3, image.height // 3), Image.ANTIALIAS)
            # wtf this is disgusting
            image.paste(overlay, (image.width // 3 * 2, image.height // 3 * 2), ImageChops.multiply(overlay, Image.new('RGBA', overlay.size, (255, 255, 255, 50))))
            final = image
        elif choice == 'nobody':
            arial = ImageFont.truetype('arial.ttf', 25)
            _, text_h = arial.getsize('No one')
        
            nobody = Image.new('RGBA', (390, text_h * 9), color='WHITE')

            draw = ImageDraw.Draw(nobody)

            draw.text((10, 10), f'''Nobody:
Not a single soul:
Not even Keanu Reeves:
Not even Big Chungus:
Not even Redditors at Area 51:

{username}:''', font=arial, fill='black')
            nobody = nobody.resize((image.width, int(image.width * nobody.height / nobody.width)), Image.ANTIALIAS)
            final = Image.new('RGBA', (image.width, image.height + nobody.height))
            final.paste(nobody, (0, 0))
            final.paste(image, (0, nobody.height))
        else:
            overlay = overlay.resize((image.width, int(image.width * overlay.height / overlay.width)), Image.ANTIALIAS)
            final = Image.new('RGBA', (image.width, image.height + overlay.height))
            final.paste(image, (0, 0))
            final.paste(overlay, (0, image.height))
        
        return save_image(final, format='PNG')

    @commands.command()
    async def reddit(self, ctx: commands.Context, *links):
        """Reddit post whoelsome"""
        return await self.basic_image_command(ctx, self.reddit_pil, ctx.author.name, filename='reddit.png')

    def clearly_pil(self, text):
        image = Image.open('assets/clearly.jpg')
        draw = ImageDraw.Draw(image)
        times = ImageFont.truetype('times.ttf', 21)
        s = draw.multiline_textsize(text, font=times)
        draw.multiline_text((image.size[0] / 2 - s[0] / 2, 330), text, fill='white', font=times, align='center')
        return save_image(image, format='JPEG', quality=50)

    @commands.command()
    @commands.cooldown(1, 5, BucketType.default)
    async def clearly(self, ctx: commands.Context, *, text):
        async with ctx.typing():
            img = await self.bot.loop.run_in_executor(None, self.clearly_pil, text)
            await ctx.send(file=discord.File(img, filename='clearly.jpg'))

    def tucker_pil(self, image):
        image: Image.Image = Image.open(io.BytesIO(image))
        tucker: Image.Image = Image.open('assets/tucker.png')
        size = image.size
        if size[0] < size[1]:
            w = size[0] // 4
            h = (tucker.size[1] * w) // tucker.size[0]
        else:
            h = size[1] // 4
            w = (tucker.size[0] * h) // tucker.size[1]
        image.paste(tucker.resize((w, h)), (size[0] - w, size[1] - h))
        return save_image(image, format='PNG')

    @commands.command()
    @commands.cooldown(1, 5, BucketType.default)
    async def tucker(self, ctx: commands.Context, *_):
        return await self.basic_image_command(ctx, self.tucker_pil, filename='tucker.png')

async def setup(bot):
    await bot.add_cog(Image_(bot))