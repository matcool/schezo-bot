from discord.ext import commands
import discord
import sqlite3 as sql
import asyncio
import pendulum

class Timezone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toTrack = []
        self.conn = sql.connect('timezones.db')

    def ensureTable(self, c):
        """Makes sure the table exists by creating it, and ignoring errors if it already exists"""
        try:
            c.execute('CREATE TABLE timezones (uid int, timezone text)')
        except Exception:
            pass

    def getUserTimezone(self, uid):
        c = self.conn.cursor()
        self.ensureTable(c)
        r = c.execute('SELECT timezone FROM timezones where uid=?', (uid,)).fetchone()
        return r[0] if r else None

    def setUserTimezone(self, uid, timezone):
        c = self.conn.cursor()
        self.ensureTable(c)
        r = c.execute('SELECT timezone FROM timezones where uid=?', (uid,)).fetchone()
        if r == None:
            c.execute('INSERT INTO timezones VALUES (?, ?)', (uid, timezone))
        else:
            c.execute('UPDATE timezones SET timezone=? WHERE uid=?', (timezone, uid))
        self.conn.commit()

    def formatTime(self, dt):
        return dt.strftime('%Y-%m-%d %H:%M')

    def tzDiff(self, a, b):
        """Returns the difference of hours of given timezones"""
        return abs(pendulum.now(a).offset - pendulum.now(b).offset) // 3600

    @commands.command()
    async def mytimeis(self, ctx, *, timezone: str=None):
        """
        Sets your timezone, so it can be used with other commands
        Timezone picker: http://scratch.andrewl.in/timezone-picker/example_site/openlayers_example.html

        Usage: {prefix}mytimeis (timezone)
        """
        if timezone == None:
            timezone = self.getUserTimezone(ctx.author.id)
            if timezone: await ctx.send(f'Your current timezone is: {timezone}\nYour time should be: {self.formatTime(pendulum.now(timezone))}')
            else: await ctx.send('You currently don\'t have a timezone set')
            return
        timezone = timezone.lower()
        for tz in pendulum.timezones:
            if tz.lower() == timezone:
                timezone = tz
                break
        else:
            return await ctx.send('Invalid timezone, please use one of these: http://scratch.andrewl.in/timezone-picker/example_site/openlayers_example.html')
        self.setUserTimezone(ctx.author.id, timezone)
        await ctx.send(f'Your timezone is now set to {timezone}\nYour local time should be: {self.formatTime(pendulum.now(timezone))}')

    @commands.command(aliases=['whattimeisitfor', 'tz'])
    async def timefor(self, ctx, *, other: discord.Member=None):
        """
        Shows what time it is for other

        Usage: {prefix}timefor [other]
        shows own time if no `other` is given
        
        {prefix}timefor Mat
        """
        # Send own if another user isn't given
        if other is None:
            timezone = self.getUserTimezone(ctx.author.id)
            if timezone: await ctx.send(f'Your current timezone is: {timezone}\nYour time should be: {self.formatTime(pendulum.now(timezone))}')
            else: await ctx.send('You currently don\'t have a timezone set')
            return

        otherTz = self.getUserTimezone(other.id)
        if otherTz == None: return await ctx.send('Could not get that user\'s timezone')
        myTz = self.getUserTimezone(ctx.author.id)
        if myTz != None:
            diff = self.tzDiff(otherTz, myTz)
            extra = f'You are {abs(diff)} hour{"s" if abs(diff) > 1 else ""} {"ahead of" if diff < 0 else "behind"} them' if diff != 0 else ''
        else: extra = ''
        await ctx.send(f'It\'s {self.formatTime(pendulum.now(otherTz))} for {other.display_name}\n{extra}')

def setup(bot):
    bot.add_cog(Timezone(bot))