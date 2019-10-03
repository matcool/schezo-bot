from discord.ext import commands
import discord
import sqlite3 as sql
from collections import namedtuple
from inspect import Parameter

StarboardInfo = namedtuple('StarboardInfo', ['guild_id', 'channel_id', 'stars_req'])

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.posted = set()
        self.conn = sql.connect('starboard.db')

    def ensure_table(self, c):
        """Makes sure the table exists by creating it, and ignoring errors if it already exists"""
        try:
            c.execute('CREATE TABLE starboard (gid int, cid int, stars int)')
        except Exception:
            pass

    def ensure_posted_table(self, c):
        """Makes sure the table exists by creating it, and ignoring errors if it already exists"""
        try:
            c.execute('CREATE TABLE posted (msgid int)')
        except Exception:
            pass

    def get_guild_starboard(self, guild_id) -> StarboardInfo:
        c = self.conn.cursor()
        self.ensure_table(c)
        r = c.execute('SELECT * FROM starboard where gid=?', (guild_id,)).fetchone()
        c.close()
        return StarboardInfo(*r) if r else None

    def set_guild_starboard(self, guild_id, channel_id, stars_req):
        c = self.conn.cursor()
        self.ensure_table(c)
        r = c.execute('SELECT * FROM starboard where gid=?', (guild_id,)).fetchone()
        if r is None:
            c.execute('INSERT INTO starboard VALUES (?, ?, ?)', (guild_id, channel_id, stars_req))
        else:
            c.execute('UPDATE starboard SET channel_id=?, stars_req=? WHERE gid=?', (channel_id, stars_req, guild_id))
        self.conn.commit()
        c.close()

    def delete_guild_starboard(self, guild_id):
        c = self.conn.cursor()
        try:
            c.execute('DELETE FROM starboard WHERE gid=?', (guild_id,))
        except sql.OperationalError:
            pass
        self.conn.commit()
        c.close()

    def add_posted_message(self, message_id):
        c = self.conn.cursor()
        self.ensure_posted_table(c)
        r = c.execute('SELECT * FROM posted WHERE msgid=?', (message_id,)).fetchone()
        if r is None:
            c.execute('INSERT INTO posted VALUES (?)', (message_id,))
            self.conn.commit()
            c.close()
            return True
        else:
            c.close()
            return False

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji != '⭐': return
        starboard = self.get_guild_starboard(reaction.message.guild.id)
        if starboard is None: return
        if starboard.channel_id == reaction.message.channel.id: return
        if reaction.count < starboard.stars_req: return

        if self.add_posted_message(reaction.message.id):
            channel = self.bot.get_channel(starboard.channel_id)
            embed = await self.make_embed(reaction.message)
            message = await channel.send(embed=embed)

    async def make_embed(self, message: discord.Message) -> discord.Embed:
        embed = discord.Embed(description=f'[Original]({message.jump_url})\n\n'+message.clean_content, colour=0xefd617)
        embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
        #embed.add_field(name=chr(0x200b), value=f'[Original]({message.jump_url})')
        url = await self.get_msg_image(message)
        if url:
            embed.set_image(url=url)
        return embed

    # copied from image_stuff
    async def get_msg_image(self, message: discord.Message) -> str:
        if message.attachments:
            for att in message.attachments:
                if att.width: return att.url
        if message.embeds:
            for embed in message.embeds:
                url = embed.thumbnail.url or embed.image.url
                if url: return url

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def starboard(self, ctx, channel_or_remove, stars: int = None):
        """
        Sets given channel as starboard channel for server
        <example>
        <cmd>#starboard 5</cmd>
        <res>Sets `#starboard` as this server's starboard channel with 5 stars required</res>
        <cmd>remove</cmd>
        <res>Removes starboard from server</res>
        </example>
        """
        if channel_or_remove.lower() == 'remove':
            self.delete_guild_starboard(ctx.guild.id)
            await ctx.send('Removed starboard from this server')
            return
        if stars is None:
            raise commands.MissingRequiredArgument(Parameter('stars', Parameter.POSITIONAL_ONLY))
        channel = await commands.TextChannelConverter().convert(ctx, channel_or_remove)
        if channel.guild != ctx.guild:
            return await ctx.send(f'Channel must be in this guild')
        if stars <= 0:
            return await ctx.send(f'Invalid star amount')
        self.set_guild_starboard(ctx.guild.id, channel.id, stars)
        await ctx.send(f'Added channel {channel} as a starboard channel')

def setup(bot):
    bot.add_cog(Starboard(bot))