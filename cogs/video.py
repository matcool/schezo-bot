import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.video import run_command, video_size, has_audio
from .utils.message import get_nearest, get_msg_video, get_msg_image
import tempfile
import os
import io
from PIL import Image
import random

class FFmpegError(Exception):
    def __init__(self, process):
        self.ret = process.ret
        self.error = process.err.decode('utf-8')

class Video(commands.Cog):
    __slots__ = 'bot',
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def basic_ffmpeg_command(self, ctx: commands.Context, ffmpeg_func, *args, filename='video.mp4', lookup=get_msg_video):
        msg = await ctx.send('Looking for video...')
        video = await get_nearest(ctx, lookup=lookup)
        if video:
            try:
                await msg.edit(content='Rendering video...')
                video = await self.bot.loop.run_in_executor(None, ffmpeg_func, video, *args)
                video = io.BytesIO(video)
                await msg.edit(content='Uploading video...')
                await ctx.send(file=discord.File(video, filename=filename))
                await msg.delete()
            except FFmpegError as error:
                await msg.edit(content=f'FFmpeg error:\n```\n{error.error[:1500]}```')
                self.bot.logger.error(error.error)
        else:
            await msg.edit(content='No video found')

    def how_ffmpeg(self, video) -> bytes:
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input')
            with open(inpath, 'wb') as file:
                file.write(video)
            outpath = os.path.join(folder, 'out.mp4') 
            cmd = [
                'ffmpeg', '-i', inpath, '-i', 'assets/how.jpg',
                '-c:v', 'h264', '-c:a', 'copy',
                '-filter_complex', '[0]scale=height=529:width=544[scaled];[1][scaled]overlay=88:0[out]', 
                '-map', '0:a?', '-map', '[out]', '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]

            process = run_command(cmd)
            if process.ret:
                raise FFmpegError(process)

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
        return await self.basic_ffmpeg_command(ctx, self.how_ffmpeg, filename='HOW.mp4')

    def keem_ffmpeg(self, video) -> bytes:
        # hard coded as to not do an unecessary ffprobe command everytime
        keem_length = 9.985
        keem_size = (118, 94)
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input')
            with open(inpath, 'wb') as file:
                file.write(video)
            outpath = os.path.join(folder, 'out.mp4') 

            size = video_size(inpath)
            if size[0] < size[1]:
                w = size[0] // 3
                h = (keem_size[1] * w) // keem_size[0]
            else:
                h = size[1] // 3
                w = (keem_size[0] * h) // keem_size[1]
            
            cmd = [
                'ffmpeg', '-i', 'assets/keem.mp4', '-i', inpath,
                '-c:v', 'h264',
                '-filter_complex', f'[0]scale=width={w}:height={h}[scaled];[1][scaled]overlay=x=main_w-overlay_w:y=0:eval=init:eof_action=endall[final];[final]pad=ceil(iw/2)*2:ceil(ih/2)*2', '-shortest',
                '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]
            # only add amix if video has audio
            # as it would error otherwise
            if has_audio(inpath):
                cmd[8] = 'amix=duration=shortest;' + cmd[8]

            process = run_command(cmd)
            if process.ret:
                raise FFmpegError(process)

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command(aliases=['keemstar', 'keemscream'])
    @commands.cooldown(2, 20, BucketType.default)
    async def keem(self, ctx):
        """
        keemstar scream
        looks for recent video and runs command on it
        """
        return await self.basic_ffmpeg_command(ctx, self.keem_ffmpeg, filename='keem.mp4')

    def vibrato_ffmpeg(self, video, f) -> bytes:
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input')
            with open(inpath, 'wb') as file:
                file.write(video)
            if not has_audio(inpath):
                return None
            outpath = os.path.join(folder, 'out.mp4') 
            cmd = [
                'ffmpeg', '-i', inpath,
                '-af', f'vibrato={f:.2f}:1,aformat=s16p', '-c:v', 'copy',
                '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]

            process = run_command(cmd)
            if process.ret:
                raise FFmpegError(process)

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command()
    @commands.cooldown(2, 20, BucketType.default)
    async def vibrato(self, ctx, modulation: float=0.5):
        """
        vibrato audio ooOoOooOOOooooOoo
        looks for recent video and runs command on it
        """
        f = modulation * 16
        if f >= 20000 or f <= 0:
            return await ctx.send(f'Modulation is too big, has to be in range of [0.1 - 1250]')
        return await self.basic_ffmpeg_command(ctx, self.vibrato_ffmpeg, f, filename='vibrato.mp4')

    def cavesounds_ffmpeg(self, image) -> bytes:
        with tempfile.TemporaryDirectory() as folder:
            inpath = os.path.join(folder, 'input.png')
            image = Image.open(io.BytesIO(image)).convert('RGB')
            size = image.size
            image.save(inpath)
            outpath = os.path.join(folder, 'out.mp4') 
            cmd = [
                'ffmpeg', '-i', f'assets/cave/cave{random.randint(0, 7)}.ogg',
                '-loop', '1', '-i', inpath,
                '-shortest', '-pix_fmt', 'yuv420p',
                '-filter_complex', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                '-f', 'mp4', outpath
            ]

            process = run_command(cmd)
            if process.ret:
                raise FFmpegError(process)

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command()
    @commands.cooldown(2, 20, BucketType.default)
    async def cavesounds(self, ctx):
        """
        minecraft cave sound to a picture
        looks for recent video and runs command on it
        """
        return await self.basic_ffmpeg_command(ctx, self.cavesounds_ffmpeg, filename='cave.mp4', lookup=get_msg_image)

def setup(bot):
    bot.add_cog(Video(bot))