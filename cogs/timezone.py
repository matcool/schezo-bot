from discord.ext import commands
import discord
import sqlite3 as sql
import asyncio
from datetime import datetime, timedelta

class Timezone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toTrack = []
        self.conn = sql.connect('timezones.db')

    def ensureTable(self, c):
        """Makes sure the table exists by creating it, and ignoring errors if it already exists"""
        try:
            c.execute('CREATE TABLE timezones (uid int, offset tinyint)')
        except Exception:
            pass

    def getUserOffset(self, uid):
        c = self.conn.cursor()
        self.ensureTable(c)
        return c.execute('SELECT offset FROM timezones where uid=?', (uid,)).fetchone()

    def setUserOffset(self, uid, offset):
        c = self.conn.cursor()
        self.ensureTable(c)
        r = c.execute('SELECT offset FROM timezones where uid=?', (uid,)).fetchone()
        if r == None:
            c.execute('INSERT INTO timezones VALUES (?, ?)', (uid, offset))
        else:
            c.execute('UPDATE timezones SET offset=? WHERE uid=?', (offset, uid))
        self.conn.commit()

    @commands.command()
    async def mytimeis(self, ctx, offset: int):
        """
        Sets your UTC offset, so it can be used with other commands
        
        Usage: s.mytimeis (offset)
        """
        if offset <= -12 or offset >= 12:
            return await ctx.send('Offset should be between -12 and 12')
        self.setUserOffset(ctx.author.id, offset)
        await ctx.send('Your offset is now set to UTC{}'.format(offset if offset < 0 else '+'+str(offset)))

    @commands.command(aliases=['whattimeisitfor'])
    async def timefor(self, ctx, other: discord.User):
        """
        Shows what time it is for other

        Usage: s.timefor (other)
        
        s.timefor Mat
        """
        otherOffset = self.getUserOffset(other.id)
        if otherOffset == None:
            return await ctx.send('Could not get that user\'s offset')
        otherOffset = otherOffset[0]
        myOffset = self.getUserOffset(ctx.author.id)
        if myOffset != None: myOffset = myOffset[0]
        otherTime = (datetime.utcnow() + timedelta(hours=otherOffset)).strftime("%Y-%m-%d %H:%M")
        extra = f'You are {abs(myOffset - otherOffset)} hours {"ahead" if myOffset - otherOffset > 0 else "behind"} them.' if myOffset != None and myOffset != otherOffset else ''
        await ctx.send(f'It\'s {otherTime} for {other.display_name}\n'+extra)
        

def setup(bot):
    bot.add_cog(Timezone(bot))