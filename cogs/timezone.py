import discord
from discord.ext import commands
import pendulum
from .utils import time as time_utils

class Timezone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.timezones

    async def add_user_timezone(self, user_id: int, timezone: str):
        return await self.db.insert_one({
            'user_id': user_id,
            'timezone': timezone
        })

    async def get_user_timezone(self, user_id: int):
        result = await self.db.find_one({'user_id': user_id})
        return result['timezone'] if result else None

    async def set_user_timezone(self, user_id: int, timezone: str):
        return await self.db.update_one({'user_id': user_id}, {'$set': {'timezone': timezone}})

    @commands.command(aliases=['set_tz', 'mytimeis'])
    async def settz(self, ctx, timezone):
        """Sets and saves your timezone"""
        timezone = time_utils.is_valid_tz(timezone, lower=True)
        if timezone is None:
            return await ctx.send('Timezone not found')
    
        result = await self.set_user_timezone(ctx.author.id, timezone)
        if result.matched_count == 0:
            await self.add_user_timezone(ctx.author.id, timezone)
        now = pendulum.now(timezone)
        await ctx.send(
            f'Your timezone is now set to {timezone}\n'
            f'Your time is {time_utils.format_date(now)}'
        )

    @commands.command(aliases=['timefor'])
    async def tz(self, ctx, *, other: discord.Member=None):
        """
        Sends what time it is for given person.
        Sends your current time info if no person is given
        """
        timezone = await self.get_user_timezone(other.id if other else ctx.author.id)
        if timezone is None:
            if other is None:
                await ctx.send("You currently don't have a timezone set\n"
                              f'Set it with `{ctx.prefix}settz <timezone>`')
            else:
                await ctx.send("Could not get that user's timezone")
        else:
            if other is None:
                await ctx.send(f'Your timezone is {timezone}\n'
                               f'Your current time is: {time_utils.format_date(pendulum.now(timezone))}')
            else:
                own_timezone = None if other is None else await self.get_user_timezone(ctx.author.id)
                response = f"It's {time_utils.format_date(pendulum.now(timezone))} for {other.display_name}"
                if own_timezone and own_timezone != timezone:
                    diff = time_utils.timezone_diff(timezone, own_timezone)
                    if diff != 0:
                        adj = 'ahead of' if diff < 0 else 'behind'
                        diff = abs(diff)
                        response += f"\nYou are {diff} hour{'s' if diff > 1 else ''} {adj} them"
                await ctx.send(response)

def setup(bot):
    bot.add_cog(Timezone(bot))