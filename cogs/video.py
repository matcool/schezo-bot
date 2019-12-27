import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.video import run_command
from .utils.message import get_nearest, get_msg_video
import tempfile
import os
import io

class Video(commands.Cog):
    __slots__ = 'bot',
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    def how_ffmpeg(self, video):
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input')
            with open(inpath, 'wb') as file:
                file.write(video)
            outpath = os.path.join(folder, 'out.mp4') 
            cmd = [
                'ffmpeg', '-i', inpath, '-i', 'assets/how.jpg', 
                '-filter_complex', '[0]scale=height=529:width=544[scaled];[1][scaled]overlay=88:0[out]', 
                '-map', '0:a?', '-map', '[out]', '-f', 'mp4', outpath
            ]

            process = run_command(cmd)
            if process.ret:
                raise Exception(f'FFmpeg returned code {process.ret}')

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command(aliases=['howvideo'])
    @commands.cooldown(2, 20, BucketType.default)
    async def howv(self, ctx):
        """
        HOW (video)
        looks for recent video and runs command on it
        """
        msg = await ctx.send('Looking for video...')
        video = await get_nearest(ctx, lookup=get_msg_video)
        if video:
            await msg.edit(content='Rendering video...')
            vid = await self.bot.loop.run_in_executor(None, self.how_ffmpeg, video)
            tmp = io.BytesIO()
            tmp.write(vid)
            tmp.seek(0)
            await msg.edit(content='Uploading video...')
            await ctx.send(file=discord.File(tmp, filename='HOW.mp4'))
            await msg.delete()
        else:
            await msg.edit(content='No video found')

def setup(bot):
    bot.add_cog(Video(bot))