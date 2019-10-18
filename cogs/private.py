import discord
from discord.ext import commands
import pendulum

class Private(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        try:
            await ctx.message.add_reaction('🆗')
        except discord.DiscordException:
            pass
        self.bot.logger.info('Logging out')
        await self.bot.logout()

    @commands.command()
    async def matfree(self, ctx):
        """How many days left for mat to be free"""
        period = pendulum.date(2019, 11, 14) - pendulum.now()
        await ctx.send(f'{period.in_days()} days left!!!')

def setup(bot):
    bot.add_cog(Private(bot))