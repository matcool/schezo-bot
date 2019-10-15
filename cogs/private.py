import discord
from discord.ext import commands

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

def setup(bot):
    bot.add_cog(Private(bot))