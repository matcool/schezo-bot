import discord
from discord.ext import commands
import textwrap
import io
from contextlib import redirect_stdout
import traceback

class Private(commands.Cog, command_attrs=dict(hidden=True)):
    __slots__ = 'bot', 
    def __init__(self, bot):
        self.bot = bot
        self.last_result = None

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        self.bot.logger.info('Logging out')
        await self.bot.logout()

    # This is highly based off https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L216
    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = code.splitlines()
        # Trim codeblock
        if code[0].startswith('```'):
            code = code[1:-1]

        # add return statement if eval is only one line
        if len(code) == 1 and not code[0].startswith('return'):
            code[0] = f'return {code[0]}'

        # use 4 spaces as it's discord code blocks indent size
        code = textwrap.indent('\n'.join(code), '    ')

        # put code in async function
        code = f"async def func():\n{code}"

        env = {
            'ctx': ctx,
            'bot': self.bot,
            'discord': discord,
            '_': self.last_result
        }
        stdout = io.StringIO()

        try:
            exec(code, env)
        except Exception as e:
            # This will most likely be a syntax error
            # since it was thrown before even running the function
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        else:
            func = env['func']
            # run function and get return and stdout
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                # save return value on _
                if ret is not None: self.last_result = ret
                # prefer stdout over function return value
                if value:
                    await ctx.send(f'```py\n{value}```')
                elif ret is not None:
                    await ctx.send(f'```py\n{repr(ret)}```')

def setup(bot):
    bot.add_cog(Private(bot))