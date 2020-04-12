import discord
from discord.ext import commands
from .utils.message import message_embed

class Starboard(commands.Cog):
    __slots__ = 'bot', 'db'
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.starboard

    async def add_guild_starboard(self, guild_id: int, channel_id: int, stars_req: int):
        return await self.db.insert_one({
            'guild_id': guild_id,
            'channel_id': channel_id,
            'stars_req': stars_req,
            'messages': []
        })

    async def get_guild_starboard(self, guild_id: int):
        return await self.db.find_one({'guild_id': guild_id})

    async def set_guild_starboard(self, guild_id: int, channel_id: int, stars_req: int):
        return await self.db.update_one({'guild_id': guild_id}, {
            '$set': {
                'channel_id': channel_id,
                'stars_req': stars_req
            }
        })

    async def add_starboard_message(self, guild_id: int, message_id: int):
        return await self.db.update_one({'guild_id': guild_id}, {'$push': {'messages': message_id}})

    async def starboard_has_message(self, guild_id: int, message_id: int):
        return await self.db.find_one({'guild_id': guild_id, 'messages': message_id}) is not None

    async def delete_guild_starboard(self, guild_id: int):
        return await self.db.delete_one({'guild_id': guild_id})

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji != '⭐': return

        starboard = await self.get_guild_starboard(reaction.message.guild.id)
        if starboard is None: return
        if starboard['channel_id'] == reaction.message.channel.id: return
        if reaction.count < starboard['stars_req']: return

        if not await self.starboard_has_message(reaction.message.guild.id, reaction.message.id):
            await self.add_starboard_message(reaction.message.guild.id, reaction.message.id)
            channel = self.bot.get_channel(starboard['channel_id'])
            embed = await message_embed(reaction.message, color=0xefd617)
            message = await channel.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def starboard(self, ctx, channel: discord.TextChannel, stars_req: int):
        """
        Sets given channel as starboard channel for server
        <examples>
        <cmd>#starboard 5</cmd>
        <res>Sets `#starboard` as this server's starboard channel with 5 stars required</res>
        <cmd>remove</cmd>
        <res>Removes starboard from server</res>
        </examples>
        """
        if stars_req <= 0:
            return await ctx.send('Invalid star amount')
        if channel.guild != ctx.guild:
            return await ctx.send("Channel isn't from this guild")

        data = await self.get_guild_starboard(ctx.guild.id)
        func = self.add_guild_starboard if data is None else self.set_guild_starboard
        await func(ctx.guild.id, channel.id, stars_req)
        await ctx.send(f'Set starboard to {channel.mention} with {stars_req} stars required')

    @starboard.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx):
        """Removes starboard from server"""
        await self.delete_guild_starboard(ctx.guild.id)
        await ctx.send("Removed this server's starboard")

    @commands.command()
    async def starcheck(self, ctx, msg: discord.Message):
        """
        Checks if a message should be in starboard and adds it.
        Works best with message links
        <examples>
        <cmd>https://discordapp.com/channels/123/123/123</cmd>
        <res>yeah</res>
        </examples>
        """
        starboard = await self.get_guild_starboard(ctx.guild.id)
        if msg.guild != ctx.guild or starboard is None or starboard['channel_id'] == msg.channel.id:
            return await ctx.send('Invalid message')
        if await self.starboard_has_message(ctx.guild.id, msg.id):
            return await ctx.send('Already on starboard')
        for reaction in msg.reactions:
            if reaction.emoji != '⭐': continue
            if reaction.count < starboard['stars_req']:
                return await ctx.send("Message doesn't meet star requirements")
            await self.add_starboard_message(ctx.guild.id, msg.id)
            channel = self.bot.get_channel(starboard['channel_id'])
            embed = await message_embed(reaction.message, color=0xefd617)
            message = await channel.send(embed=embed)
            return await ctx.send('Added to starboard')
        await ctx.send("Message doesn't meet star requirements")

def setup(bot):
    bot.add_cog(Starboard(bot))