import discord
from discord.ext import commands

from .utils.message import get_nearest

from PIL import Image
import io

# class name is Image_ as to not intefere with PIL's Image class
class Image_(commands.Cog, name='Image'):
    def __init__(self, bot):
        self.bot = bot

    def howpil(self, image: bytes):
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
                img = await self.bot.loop.run_in_executor(None, self.howpil, image)
                await ctx.send(file=discord.File(img, filename='HOW.jpeg'))
            else:
                await ctx.send('No image found')

def setup(bot):
    bot.add_cog(Image_(bot))