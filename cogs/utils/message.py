import discord
from discord.ext import commands
from .http import get_file_size, get_file_type, get_page
from typing import Union, Callable

async def get_avatar(user: discord.User, url: bool=False) -> Union[bytes, str]:
    avatar = user.avatar_url_as(format='png')
    return str(avatar) if url else await avatar.read()

async def get_msg_image(message: discord.Message, url: bool=False) -> Union[bytes, str]:
    if message.attachments:
        for att in message.attachments:
            file_type = await get_file_type(att.url)
            if file_type and file_type.startswith('image/') and 'svg' not in file_type:
                return att.url if url else await att.read()
    if message.embeds:
        for embed in message.embeds:
            url_str = embed.thumbnail.url or embed.image.url
            if url_str: return url_str if url else await get_page(url_str)

ALLOWED_VIDEOS = {'mp4', 'mkv', 'wmv', 'avi', 'webm'}

async def get_msg_video(message: discord.Message, max_size: int=8000000, url: bool=False) -> Union[bytes, str]:
    if message.attachments:
        for att in message.attachments:
            ext = att.filename.split('.')[-1]
            if att.size < max_size and ext in ALLOWED_VIDEOS:
                return att.url if url else await att.read()
    if message.embeds:
        for embed in message.embeds:
            if embed.video.url:
                size = await get_file_size(embed.video.url)
                if size and size < max_size:
                    return embed.video.url if url else await get_page(embed.video.url)

async def get_nearest(ctx: commands.Context, limit: int=10, lookup: Callable[[discord.Message], Union[bytes, str]]=get_msg_image, **lookup_kwargs) -> Union[bytes, str]:
    look = await lookup(ctx.message, **lookup_kwargs)
    if look is None:
        async for message in ctx.history(limit=limit):
            if message.id == ctx.message.id: continue
            look = await lookup(message, **lookup_kwargs)
            if look is not None: break
    return look

async def message_embed(message: discord.Message, original: bool=True, color: int=0xa3a3a3, timestamp: bool=True, attachments: bool=True) -> discord.Embed:
    embed = discord.Embed(description=message.clean_content, colour=color)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    if original:
        embed.description = f'[Original]({message.jump_url})\n\n' + embed.description
    if timestamp:
        embed.timestamp = message.created_at
    url = await get_msg_image(message, url=True)
    if url:
        embed.set_image(url=url)
    if attachments and message.attachments:
        fancy = '\n'.join(f'- [{att.filename}]({att.url})' for att in message.attachments if att.url != url)
        if fancy: embed.add_field(name='Attachments', value=fancy)
    return embed