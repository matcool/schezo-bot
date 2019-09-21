from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import aiohttp
import tempfile
import os
import subprocess
import io
from collections import namedtuple

ProcessInfo = namedtuple('ProcessInfo', ['out', 'err', 'ret'])

def run_command(cmd, input=None):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(input)
    ret = process.poll()
    return ProcessInfo(out, err, ret)

def video_length(video_path):
    process = run_command((
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ))
    if process.ret: raise Exception('FFmpeg error: ' + str(process.err, encoding='utf-8'))
    return float(process.out)

def video_size(video_path):
    process = run_command((
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', video_path
    ))
    if process.ret: raise Exception('FFmpeg error: ' + str(process.err, encoding='utf-8'))
    return tuple(map(int, str(process.out, encoding='utf-8').strip().split('x')))

def has_audio(video_path):
    process = run_command((
        'ffprobe', '-i', video_path, '-show_streams', '-select_streams', 'a', '-v', 'error'
    ))
    if process.ret: raise Exception('FFmpeg error: ' + str(process.err, encoding='utf-8'))
    return bool(process.out)

# Video file extensions allowed in the get_msg_video
ALLOWED = {'mp4', 'mkv', 'wmv', 'avi', 'webm'}

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

        > {prefix}howv
        either does it with the given video or looks for an video in the past 10 messages
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

    @staticmethod
    def keemffmpeg(video):
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
                'ffmpeg', '-i', 'stuff/keem.mp4', '-i', inpath,
                '-filter_complex', f'[0]scale=width={w}:height={h}[scaled];[1][scaled]overlay=x=main_w-overlay_w:y=0:eval=init:eof_action=endall', '-shortest',
                '-f', 'mp4', outpath,
                '-hide_banner', '-v', 'error'
            ]
            # only add amix if video has audio
            # as it would error otherwise
            if has_audio(inpath):
                cmd[6] = 'amix=duration=shortest;' + cmd[6]

            process = run_command(cmd)
            if process.ret:
                raise Exception(f'FFmpeg returned with error code {process.ret}')

            with open(outpath, 'rb') as file:
                data = file.read()
        return data

    @commands.command(aliases=['keemstar', 'keemscream'])
    @commands.cooldown(2, 20, BucketType.default)
    async def keem(self, ctx):
        """
        Make keemstar scream to given video

        > {prefix}keem
        either does it with the given video or looks for an video in the past 10 messages
        """
        msg = await ctx.send('Looking for video...')
        video = await self.get_nearest_video(ctx)
        if video:
            await msg.edit(content='Rendering video...')
            vid = await self.bot.loop.run_in_executor(None, self.keemffmpeg, video)
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