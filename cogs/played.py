import discord
from discord.ext import commands, buttons
import asyncio
from .utils.misc import buttons_mixin
from .utils.time import format_time
from typing import Set

buttons_mixin(buttons)

class PlayingTracker(commands.Cog, name='Playing Tracker'):
    __slots__ = 'bot', 'db', 'task', 'to_track'
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.played
        self.task = asyncio.create_task(self.update_playing())
        self.to_track: Set[int] = set()

    def cog_unload(self):
        self.task.cancel()

    """
    {
        _id: ObjectID(whatever),
        user_id: the user id,
        played: [
            {
                name: activity name,
                time: time in minutes
            },
            (etc)
        ]
    }
    """

    async def update_playing(self):
        await self.get_to_track()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            for user in self.to_track:
                member = discord.utils.get(self.bot.get_all_members(), id=user)
                if member is None: continue

                # ignore custom status if playing anything, else just use custom status
                activities = tuple(filter(lambda a: a.type != 4, member.activities))
                act = activities[0] if len(activities) != 0 else member.activity
                if act is None: continue

                await self.update_game(user, act)

    async def get_to_track(self):
        cursor = self.db.find({}, ['user_id'])
        self.to_track = set()
        async for entry in cursor:
            self.to_track.add(entry['user_id'])

    async def track(self, user_id: int):
        self.to_track.add(user_id)
        return await self.db.insert_one({
            'user_id': user_id,
            'played': []
        })

    async def update_game(self, user_id: int, activity: discord.Activity):
        # sadly couldn't do all this in one query :sob:
        result = await self.db.find_one_and_update({
            'user_id': user_id,
            'played': {
                '$elemMatch': {'name': activity.name}
            }
        }, {'$inc': {'played.$.time': 1}})
        if result is None:
            await self.db.update_one({'user_id': user_id}, {
                '$push': {
                    'played': {
                        'name': activity.name,
                        'time': 1
                    }
                }
            })
        
    async def get_user_played(self, user_id: int):
        result = await self.db.find_one({'user_id': user_id})
        return result['played'] if result else None

    async def stop_tracking(self, user_id: int):
        if user_id not in self.to_track: return False
        self.to_track.remove(user_id)
        await self.db.delete_one({'user_id': user_id})
        return True

    @commands.group(invoke_without_command=True)
    async def played(self, ctx, user: discord.Member=None):
        """
        Check played games stats
        <examples>
        <cmd></cmd>
        <res>Shows your played games</res>
        <cmd>@Joe</cmd>
        <res>Shows Joe's played games</res>
        <cmd>enable</cmd>
        <res>Enables game tracking for you</res>
        <cmd>delete</cmd>
        <res>Disables tracking and deletes tracked data</res>
        </examples>
        """
        if user and user.id not in self.to_track:
            await ctx.send('Tagged person does not have played tracking enabled')
            return

        if user is None: user = ctx.author

        games = await self.get_user_played(user.id)
        if games is None:
            return await ctx.send(f"{'You' if user == ctx.author else 'They'} don't have playing tracking on")
        elif len(games) < 1:
            return await ctx.send(f"{'You' if user == ctx.author else 'They'} haven't played any games yet")

        games.sort(key=lambda x: x['time'], reverse=True)

        per_page = 10
        pages = [games[i:i+per_page] for i in range(0, len(games), per_page)]
        pages = ['\n'.join(f"**{game['name']}** - {format_time(game['time']*60)}" for game in page) for page in pages]

        paginator = buttons.Paginator(title=f"{user.name}'s played stats", colour=0x61C7C3, embed=True, timeout=10, use_defaults=True,
        entries=pages, length=1)
        await paginator.start(ctx)

    @played.command()
    async def enable(self, ctx):
        if ctx.author.id in self.to_track:
            await ctx.send('Already tracking')
        else:
            await self.track(ctx.author.id)
            await ctx.send(f"I'm now tracking your games\nUse `{ctx.prefix}played delete` to stop tracking and delete data")

    @played.command()
    async def delete(self, ctx):
        res = await self.stop_tracking(ctx.author.id)
        if not res:
            await ctx.send("I'm not tracking your games")
        else:
            await ctx.send('Game tracking is now disabled')

def setup(bot):
    bot.add_cog(PlayingTracker(bot))