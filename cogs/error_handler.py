import discord
from discord.ext import commands
from .utils.misc import string_distance
from .utils.time import format_time
import logging
import traceback
import asyncio

class ErrorHandlerCog(commands.Cog):
    __slots__ = 'bot', 'ignored', 'logger'
    def __init__(self, bot):
        self.bot = bot
        self.ignored = (commands.NotOwner, commands.DisabledCommand, discord.errors.Forbidden)
        self.logger = logging.getLogger('schezo')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, self.ignored):
            return

        elif isinstance(error, commands.CommandNotFound):
            cmds = [cmd.name for cmd in self.bot.commands if not cmd.hidden]
            cmds.sort(key=lambda x: string_distance(x, ctx.invoked_with))
            msg = await ctx.send(f'Unknown command! Did you mean {cmds[0]}?')
            await asyncio.sleep(5)
            await msg.delete()
            
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('{} is a required argument that is missing.'.format(error.param.name))
            
        elif isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f'Command on cooldown! Please wait {format_time(round(error.retry_after,1))}.')
            
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error.args[0])
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f'Missing permissions: {", ".join(error.missing_perms)}')

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f'Bot has missing permissions: {", ".join(error.missing_perms)}')

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command is guild only')
        
        else:
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            tb = ''.join(tb)
            self.logger.error(f'Error on command: {ctx.command.name}\n'
                          f'Message: {ctx.message.content}\n'
                          f'Traceback: {tb}')
            await ctx.send('Internal error')

async def setup(bot):
    await bot.add_cog(ErrorHandlerCog(bot))