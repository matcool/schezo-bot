import discord
from discord.ext import commands, buttons
import asyncio
from .utils.misc import buttons_mixin
from .utils.time import format_time

buttons_mixin(buttons)

class PlayingTracker(commands.Cog, name='Playing Tracker'):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.played
        self.task = asyncio.create_task(self.update_playing())
        # A list of (user_id, guild_id)
        # guild_id is required as you cannot get an user's activty, only a member's
        self.to_track = []

    def cog_unload(self):
        self.task.cancel()

    """
    {
        _id: ObjectID(whatever),
        user_id: the user id,
        guild_id: guild which the user is in,
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
        await self.bot.wait_until_ready()
        await self.get_to_track()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            # user is a tuple of (user_id, guild_id)
            for user in self.to_track:
                guild = self.bot.get_guild(user[1])
                if guild is None: continue

                member = guild.get_member(user[0])
                if member is None: continue

                act = member.activity
                if act is None: continue

                await self.update_game(user[0], act)

    async def get_to_track(self):
        cursor = self.db.find({}, ['user_id', 'guild_id'])
        self.to_track = []
        async for entry in cursor:
            self.to_track.append((entry['user_id'], entry['guild_id']))

    async def track(self, user_id: int, guild_id: int):
        self.to_track.append((user_id, guild_id))
        return await self.db.insert_one({
            'user_id': user_id,
            'guild_id': guild_id,
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

    def to_track_index(self, user_id: int):
        i = tuple(j for j,i in enumerate(self.to_track) if i[0] == user_id)
        if len(i) != 0: return i[0]

    async def stop_tracking(self, user_id: int):
        index = self.to_track_index(user_id)
        if index is None: return False
        self.to_track.pop(index)
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
        if user and not any(map(lambda x: x[0] == user.id, self.to_track)):
            await ctx.send('Tagged person does not have played tracking enabled')
            return

        if user is None: user = ctx.author

        games = await self.get_user_played(user.id)
        if games is None:
            return await ctx.send(f"{'You' if user == ctx.author else 'They'} don't have playing tracking on")
        elif len(games) < 1:
            return await ctx.send(f"{'You' if user == ctx.author else 'They'} haven't played any games yet")

        games.sort(key=lambda x: x['time'], reverse=True)
        pages = []
        page = ''
        i = 0
        for game in games:
            page += f"**{game['name']}** - {format_time(game['time']*60)}\n"
            i += 1
            if i > 10:
                i = 0
                pages.append(page)
                page = ''
        if i != 0: pages.append(page)
        paginator = buttons.Paginator(title=f"{user.name}'s played stats", colour=0x61C7C3, embed=True, timeout=10, use_defaults=True,
        entries=pages, length=1)
        await paginator.start(ctx)

    @played.command()
    async def enable(self, ctx):
        if self.to_track_index(ctx.author.id) is not None:
            await ctx.send('Already tracking')
        else:
            await self.track(ctx.author.id, ctx.guild.id)
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