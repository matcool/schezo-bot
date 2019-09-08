from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import aiohttp
import tempfile
import os
import subprocess
import io

class VideoStuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_page(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

    async def get_file_size(self, url) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                size = response.headers.get('Content-Length')
        if size: return int(size)

    async def get_msg_video(self, message: discord.Message, max_size=8000000) -> bytes:
        ALLOWED = {'mp4', 'mkv', 'wmv', 'avi'}
        if message.attachments:
            for att in message.attachments:
                if att.size < max_size and att.filename.split('.')[-1] in ALLOWED: return await att.read()
        if message.embeds:
            for embed in message.embeds:
                if embed.video.url:
                    size = await self.get_file_size(embed.video.url)
                    if size and size < max_size:
                        return await self.get_page(embed.video.url)
    
    async def get_nearest_video(self, ctx, limit=10) -> bytes:
        video = await self.get_msg_video(ctx.message)
        if video is None:
            async for message in ctx.history(limit=limit):
                if message.id == ctx.message.id: continue
                video = await self.get_msg_video(message)
                if video is not None: break
        return video

    @staticmethod
    def howffmpeg(video):
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input')
            with open(inpath, 'wb') as file:
                file.write(video)
            outpath = os.path.join(folder, 'out.mp4') 
            cmd = [
                'ffmpeg', '-i', inpath, '-i', 'stuff/how.jpg', 
                '-filter_complex', '[0]scale=height=529:width=544[scaled];[1][scaled]overlay=88:0[out]', 
                '-map', '0:a?', '-map', '[out]', '-f', 'mp4', outpath
            ]
            # Running the command
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate(None)
            retcode = process.poll()
            if retcode:
                raise Exception(f'FFmpeg returned code {retcode}')

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command(aliases=['howvideo'])
    @commands.cooldown(2, 20, BucketType.default)
    async def howv(self, ctx):
        """
        HOW (video)

        > {prefix}howv
        either does it with the given video or looks for an video in the past 10 messages
        video cannot be a link (prob will change)
        """
        msg = await ctx.send('Looking for video...')
        video = await self.get_nearest_video(ctx)
        if video:
            await msg.edit(content='Rendering video...')
            vid = await self.bot.loop.run_in_executor(None, self.howffmpeg, video)
            tmp = io.BytesIO()
            tmp.write(vid)
            tmp.seek(0)
            await msg.edit(content='Uploading video...')
            await ctx.send(file=discord.File(tmp, filename='HOW.mp4'))
            await msg.delete()
        else:
            await msg.edit(content='No video found')

def setup(bot):
    bot.add_cog(VideoStuff(bot))