import discord
import traceback
#import sys
from discord.ext import commands

#https://github.com/TheAlgorithms/Python/blob/master/strings/levenshtein_distance.py
def string_distance(a, b):
    if len(a) < len(b): return string_distance(b, a)
    if len(b) == 0: return len(a)
    prow = range(len(b) + 1)
    for i, c1 in enumerate(a):
        crow = [i + 1]
        for j, c2 in enumerate(b):
            ins = prow[j + 1] + 1
            dl = crow[j] + 1
            sub = prow[j] + (c1 != c2)
            crow.append(min(ins, dl, sub))
        prow = crow
    return prow[-1]

class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.noperm = bot.get_emoji(321784861595664385)

    ignored = (commands.NotOwner,commands.DisabledCommand)
    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error,self.ignored):
            return

        if isinstance(error,commands.CommandNotFound):
            cmds = list(map(lambda x: x.name, self.bot.commands))
            cmds.sort(key=lambda x: string_distance(x,ctx.invoked_with))
            await ctx.send(f'Unknown command! Did you mean {cmds[0]}?')
            return

        if isinstance(error,discord.errors.Forbidden):
            try:
                await ctx.message.add_reaction(self.noperm)
            except discord.errors.Forbidden:
                return

        if isinstance(error,commands.MissingRequiredArgument):
            await ctx.send('{} is a required argument that is missing.'.format(error.param))
            return

        if isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f'Command on cooldown! Please wait {round(error.retry_after,1)} seconds.')
            return
        
        print('Ignoring exception in command {}:'.format(ctx.command))
        traceback.print_exception(type(error), error, error.__traceback__)
        #print(error)
        #print("error line {}".format(sys.exc_info()[-1].tb_lineno))

def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
