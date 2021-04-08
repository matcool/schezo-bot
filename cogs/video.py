import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.video import run_command, video_size, has_audio
from .utils.message import get_nearest, get_msg_video, get_msg_image, get_msg_video_or_img
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

    @staticmethod
    def _sound_ffmpeg(media, media_type: str, sound: str):
        ext = 'webm' if media_type == 'video' else 'mp4'
        with tempfile.TemporaryDirectory() as folder:
            outpath = os.path.join(folder, 'out.' + ext)
            # enums?? what are those
            if media_type == 'image':
                inpath = os.path.join(folder, 'input.png')
                Image.open(io.BytesIO(media)).convert('RGB').save(inpath)

                cmd = [
                    'ffmpeg', '-i', sound,
                    '-loop', '1', '-i', inpath,
                    '-shortest', '-pix_fmt', 'yuv420p',
                    '-filter_complex', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                    '-c:v', 'mpeg4',
                    '-f', 'mp4', outpath
                ]
            elif media_type == 'video':
                inpath = os.path.join(folder, 'input')
                with open(inpath, 'wb') as file:
                    file.write(media)

                cmd = [
                    'ffmpeg', '-v', 'error',
                    '-i', inpath,
                    '-i', sound,
                    '-map', '0:v',
                    '-map', '1:a',
                    '-shortest',
                    '-f', 'webm', outpath
                ]
            else:
                # ???
                raise Exception(f'What {media_type!r}')

            process = run_command(cmd)
            if process.ret:
                raise FFmpegError(process)

            with open(outpath, 'rb') as file:
                data = file.read()
        return (data, ext)

    async def sound_ffmpeg_command(self, ctx: commands.Context, sound: str, filename: str='video'):
        msg = await ctx.send('Looking for media...')
        media = await get_nearest(ctx, lookup=get_msg_video_or_img)
        if media:
            try:
                await msg.edit(content='Rendering video...')
                video, ext = await self.bot.loop.run_in_executor(None, self._sound_ffmpeg, media[0], media[1], sound)
                video = io.BytesIO(video)
                await msg.edit(content='Uploading video...')
                await ctx.send(file=discord.File(video, filename=filename + f'.{ext}'))
                await msg.delete()
            except FFmpegError as error:
                await msg.edit(content=f'FFmpeg error:\n```\n{error.error[:500]}```')
                self.bot.logger.error(error.error)
        else:
            await msg.edit(content='No media found')

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

    @commands.command(aliases=['cave'])
    @commands.cooldown(2, 20, BucketType.default)
    async def cavesounds(self, ctx):
        """
        minecraft cave sound to a picture
        looks for recent image/video and runs command on it
        """
        return await self.sound_ffmpeg_command(ctx, f'assets/cave/cave{random.randint(0, 7)}.mp3', filename='cave')

    @commands.command(aliases=['fnaf'])
    @commands.cooldown(2, 20, BucketType.default)
    async def fnafsounds(self, ctx, fnaf=None):
        """
        fnaf sound
        looks for recent image/video and runs command on it

        `fnaf` can be either set to `1`, `2`, `3`, `4`, `6`, `sl` or `ucn`. defaults to random
        """
        options = ('1', '2', '3', '4', '6', 'sl', 'ucn')
        if fnaf is None or fnaf not in options:
            fnaf = random.choice(options)
        folder = os.path.join('assets/fnaf', fnaf)
        sounds = os.listdir(folder)
        sound = os.path.join(folder, random.choice(sounds))
        return await self.sound_ffmpeg_command(ctx, sound, filename='fnaf')

    @commands.command(aliases=['amongus'])
    @commands.cooldown(2, 20, BucketType.default)
    async def amongussounds(self, ctx, sfx=None):
        """among us sound fx on video or img"""
        options = ('amongus', 'death', 'drip', 'report', 'vent')
        if sfx not in options:
            sfx = random.choice(options)
        return await self.sound_ffmpeg_command(ctx, f'assets/amongus/{sfx}.mp3', filename='amongus')

def setup(bot):
    bot.add_cog(Video(bot))