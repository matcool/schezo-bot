from discord.ext import commands
import discord
from typing import Tuple, Dict, List
import re

class CustomHelp(commands.Cog):
    __slots__ = 'bot',
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    def commands_dict(self) -> Dict[str, List[commands.Command]]:
        final = {}
        for cogname, cog in self.bot.cogs.items():
            if hasattr(cog, 'overwrite_name'):
                cogname = cog.overwrite_name
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    if cogname not in final:
                        final[cogname] = []
                    final[cogname].append(cmd)
        final = dict(sorted(final.items(), key=lambda i: len(i[1]), reverse=True))
        return final

    @commands.command(name='help', hidden=True)
    async def _help(self, ctx, lookup=None, *subcommands):
        """
        Shows help for given command or
        lists all/category commands
        Examples::
        > 
        Sends an embed listing all commands
        > money
        Sends help and info for command *money*
        """
        # Show all cogs and their commands WITHOUT short doc
        if lookup is None:
            cmds = self.commands_dict()

            # Sort by name
            for category in cmds:
                cmds[category].sort(key=lambda c: c.name)

            embed = discord.Embed(title='**Commands**',colour=0x3498db)
            for cog in cmds:
                formatted_cmds = ' '.join(map(lambda cmd: f'`{cmd.name}`', cmds[cog]))
                embed.add_field(name=cog, value=formatted_cmds, inline=False)
            await ctx.send(embed=embed)

        # Look up command
        else:
            cmd = self.bot.get_command(' '.join([lookup.lower(), *map(str.lower, subcommands)]))
            if cmd:
                cmd_help = cmd.help
                examples = None
                if cmd_help:
                    examples = ''
                    final_help = ''
                    in_example = False
                    for line in cmd_help.splitlines():
                        if not in_example:
                            if line == 'Examples::':
                                in_example = True
                                final_help = final_help[:-1]
                            else:
                                final_help += line + '\n'
                        else:
                            if line[0] == '>':
                                examples += f'`> {ctx.prefix}{cmd.qualified_name} {line[2:]}`\n'
                            else:
                                examples += line + '\n'
                    cmd_help = final_help
                    examples = examples[:-1]
                        
                embed = discord.Embed(
                    title=cmd.qualified_name,
                    description=cmd_help,
                    colour=0x87ef73
                    )
                embed.add_field(name='Syntax', value=f'`{ctx.prefix}{cmd.qualified_name} {cmd.signature}`')
                if cmd.aliases:
                    embed.add_field(name='Aliases', value=' '.join(map(lambda x: f'`{x}`', cmd.aliases)))
                if isinstance(cmd, commands.Group):
                    embed.add_field(name='Subcommands', value=' '.join(f'`{i.name}`' for i in cmd.commands))
                if examples:
                    embed.add_field(name='Examples', value=examples, inline=False)
                await ctx.send(embed=embed)
            else:
                return await ctx.send('Command not found')

def setup(bot):
    bot.add_cog(CustomHelp(bot))