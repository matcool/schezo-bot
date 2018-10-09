import discord
import traceback
#import sys
from discord.ext import commands


class ErrorHandlerCog:
    def __init__(self, bot):
        self.bot = bot
        self.noperm = bot.get_emoji(321784861595664385)

    ignored = (commands.CommandNotFound, commands.NotOwner)
    async def on_command_error(self,ctx,error):
        if isinstance(error,self.ignored):
            return

        
        if isinstance(error,discord.errors.Forbidden):
            try:
                await ctx.message.add_reaction(self.noperm)
            except discord.errors.Forbidden:
                return
        elif isinstance(error,commands.MissingRequiredArgument):
            await ctx.send('{} is a required argument that is missing.'.format(error.param))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command))
            traceback.print_exception(type(error), error, error.__traceback__)
            #print(error)
            #print("error line {}".format(sys.exc_info()[-1].tb_lineno))

def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
