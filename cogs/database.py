from discord.ext import commands
import sqlite3 as sql
import asyncio
from functools import partial

class PlayedTracker:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.checkPlaying())
        self.toTrack = []
        self.conn = None

    async def checkPlaying(self):
        await self.bot.wait_until_ready()
        self.conn = sql.connect('playing.db')
        self.getTrackList()
        while not self.bot.is_closed():
            for n in self.toTrack:
                try:
                    mem = self.bot.get_guild(n[1]).get_member(n[0])
                except AttributeError:
                    continue
                if mem is None:
                    continue

                if len(mem.activities) < 1:
                    continue
                act = mem.activities[0]
                self.updateGame(n[0],act.name,act.type.value)
                print(f'Updated {n[0]} who was playing {mem.activities[0].name}')
            self.conn.commit()
            print('Done!')
            await asyncio.sleep(60)

    def getTrackList(self):
        c = self.conn.cursor()
        try:
            c.execute('CREATE TABLE tracklist (uid int, guildid int)')
        except Exception:
            pass
        self.toTrack = c.execute('SELECT * FROM tracklist').fetchall()

    def track(self,uid,gid):
        self.toTrack.append((uid,gid))
        c = self.conn.cursor()
        c.execute('INSERT INTO tracklist VALUES (?, ?)',(uid,gid))
        self.conn.commit()

    def updateGame(self,uid,game,acttype):
        c = self.conn.cursor()
        uid = 'u'+str(uid)
        try:
            c.execute(f'CREATE TABLE {uid} (game text, time int, acttype tinyint)')
        except Exception:
            pass
        c.execute(f'SELECT * FROM {uid} WHERE game=?', (game,))
        if c.fetchone() == None:
            c.execute(f'INSERT INTO {uid} VALUES (?, ?, ?)', (game,1,acttype))
            return
        time = c.execute(f'SELECT time FROM {uid} WHERE game=?', (game,)).fetchone()[0]
        c.execute(f'UPDATE {uid} SET time=? WHERE game=?',(time+1,game))
        
    def getUserPlayed(self,uid):
        c = self.conn.cursor()
        uid = 'u'+str(uid)
        try:
            c.execute(f'SELECT time FROM {uid}')
        except Exception:
            return
        return c.execute(f'SELECT * FROM {uid}').fetchall()

    def formatTime(self,time,acttype):
        verb = 'played streamed listened watched ????'.split(' ')[acttype]
        hours,minutes = divmod(time,60)
        days,hours = divmod(hours,24)
        time = ''
        time += f'{days}d' if days > 0 else ''
        time += f'{hours}h' if hours > 0 else ''
        time += f'{minutes}m' if minutes > 0 else ''
        return f'{verb} for {time}'

    @commands.command()
    async def played(self,ctx,join=None):
        if (ctx.author.id,ctx.guild.id) not in self.toTrack:
            if join is None:
                await ctx.send(f'I\'m currently not tracking your games, do `{self.bot.command_prefix}played yes` to join')
                return
            else:
                self.track(ctx.author.id,ctx.guild.id)
                await ctx.send('Your games will now be tracked forever!!! >:) :smiling_imp:')
                return

        games = self.getUserPlayed(ctx.author.id)
        if games is None or len(games) < 1:
            await ctx.send('You haven\'t played any games yet!')
            return

        games.sort(key=lambda x: x[1],reverse=True)
        await ctx.send('\n'.join([f'{i[0]} - {self.formatTime(*i[1:])}' for i in games]))






def setup(bot):
    bot.add_cog(PlayedTracker(bot))