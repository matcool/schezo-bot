import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.video import run_command, video_size, has_audio
from .utils.message import get_nearest, get_msg_video
import tempfile
import os
import io

class Video(commands.Cog):
    __slots__ = 'bot',
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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
                self.bot.logger.error(process.err.decode('utf-8'))
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
            vid = io.BytesIO(vid)
            await msg.edit(content='Uploading video...')
            await ctx.send(file=discord.File(vid, filename='HOW.mp4'))
            await msg.delete()
        else:
            await msg.edit(content='No video found')

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
                '-filter_complex', f'[0]scale=width={w}:height={h}[scaled];[1][scaled]overlay=x=main_w-overlay_w:y=0:eval=init:eof_action=endall', '-shortest',
                '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]
            # only add amix if video has audio
            # as it would error otherwise
            if has_audio(inpath):
                cmd[8] = 'amix=duration=shortest;' + cmd[8]

            process = run_command(cmd)
            if process.ret:
                self.bot.logger.error(process.err.decode('utf-8'))
                raise Exception(f'FFmpeg returned with error code {process.ret}')

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
        msg = await ctx.send('Looking for video...')
        video = await get_nearest(ctx, lookup=get_msg_video)
        if video:
            await msg.edit(content='Rendering video...')
            vid = await self.bot.loop.run_in_executor(None, self.keem_ffmpeg, video)
            vid = io.BytesIO(vid)
            await msg.edit(content='Uploading video...')
            await ctx.send(file=discord.File(vid, filename='keem.mp4'))
            await msg.delete()
        else:
            await msg.edit(content='No video found')

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
                '-af', f'vibrato={f:.2f}:1', '-c:v', 'copy',
                '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]

            process = run_command(cmd)
            if process.ret:
                self.bot.logger.error(process.err.decode('utf-8'))
                raise Exception(f'FFmpeg returned code {process.ret}')

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command()
    @commands.cooldown(2, 20, BucketType.default)
    async def vibrato(self, ctx, ondulation: float=0.5):
        """
        vibrato audio ooOoOooOOOooooOoo
        looks for recent video and runs command on it
        """
        msg = await ctx.send('Looking for video...')
        video = await get_nearest(ctx, lookup=get_msg_video)
        if video:
            await msg.edit(content='Rendering video...')
            f = ondulation * 16
            vid = await self.bot.loop.run_in_executor(None, self.vibrato_ffmpeg, video, f)
            if vid is None:
                return await ctx.send('Video has no audio')
            vid = io.BytesIO(vid)
            await msg.edit(content='Uploading video...')
            await ctx.send(file=discord.File(vid, filename='vibrato.mp4'))
            await msg.delete()
        else:
            await msg.edit(content='No video found')

def setup(bot):
    bot.add_cog(Video(bot))