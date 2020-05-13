from .utils.message import message_embed
from discord.ext import commands
import discord
import asyncio
import re

class Option:
    __slots__ = ('default', 'type', 'description')
    def __init__(self, default, _type, description: str):
        self.default = default
        self.type = _type
        self.description = description

class GuildFeatures(commands.Cog):
    __slots__ = ('bot', 'db', 'overwrite_name', 'active_guilds')

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.guild_features
        self.overwrite_name = 'Utility'
        self.default_config = {
            'quote_links': Option(False, bool, 'Automatically quotes message links sent in chat')
        }
        self.active_guilds = set()
        asyncio.create_task(self.get_active_guilds())
        self.msg_link_regex = re.compile(r'^https?://(?:(ptb|canary)\.)?discord(?:app)?\.com/channels/\d{15,21}/(?P<channel_id>\d{15,21})/(?P<message_id>\d{15,21})/?$')

    def defaults(self):
        return dict((key, value.default) for key, value in self.default_config.items())

    async def get_active_guilds(self):
        async for guild in self.db.find({}):
            self.active_guilds.add(guild['id'])

    async def init_guild(self, guild_id: int):
        self.active_guilds.add(guild_id)
        return await self.db.insert_one({
            'id': guild_id,
            **self.defaults()
        })

    async def remove_guild(self, guild_id: int):
        self.active_guilds.discard(guild_id)
        await self.db.delete_one({'id': guild_id})

    async def get_guild(self, guild_id: int):
        return await self.db.find_one({'id': guild_id})

    async def get_option(self, guild_id: int, option: str):
        return (await self.db.find_one({'id': guild_id}, {option: True})).get(option, self.default_config[option].default)

    async def update_guild(self, guild_id: int, update):
        return await self.db.update_one({'id': guild_id}, update)

    async def get_message_from_url(self, url: str) -> discord.Message:
        # mostly stolen from https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/converter.py#L194
        match = self.msg_link_regex.match(url)
        if not match: return
        channel_id = int(match.group('channel_id'))
        message_id = int(match.group('message_id'))
        message = self.bot._connection._get_message(message_id)
        if message: return message
        channel = self.bot.get_channel(channel_id)
        if not channel: return
        try:
            return await channel.fetch_message(message_id)
        except (discord.NotFound, discord.Forbidden):
            return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id not in self.active_guilds: return
        if await self.get_option(message.guild.id, 'quote_links'):
            msg = await self.get_message_from_url(message.content)
            if msg:
                try:
                    await message.channel.send(embed=await message_embed(msg))
                    await message.delete()
                except discord.Forbidden:
                    pass

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx, key: str=None, *, value=None):
        if key is None:
            embed = discord.Embed(title='Guild settings')
            guild = await self.get_guild(ctx.guild.id)
            if guild is None:
                guild = {}
                embed.description = '*guild not enabled, showing defaults*'
            defaults = self.defaults()
            embed.add_field(name='Options', value='\n'.join(f'`{k}` - `{guild.get(k, defaults[k])}`' for k in self.default_config.keys()))
            await ctx.send(embed=embed)
        else:
            guild = await self.get_guild(ctx.guild.id)
            if guild is None:
                await ctx.send('Initializing config...')
                await self.init_guild(ctx.guild.id)
                guild = {}
            option = self.default_config.get(key)
            if option is None:
                return await ctx.send('Option not found')
            val = guild.get(key, option.default)
            if option.type == bool:
                await self.update_guild(ctx.guild.id, {'$set': {key: not val}})
                return await ctx.send(f'`{key}` is now **{"off" if val else "on"}**')

    @config.command(name='help')
    async def help_(self, ctx, option: str):
        _option = option
        option: Option = self.default_config.get(option)
        if option is None:
            return await ctx.send('Option not found')
        embed = discord.Embed(title=f'`{_option}`', description=option.description)
        embed.add_field(name='Default value', value=f'`{option.default}`')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildFeatures(bot))