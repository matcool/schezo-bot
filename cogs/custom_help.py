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
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    if final.get(cogname) == None:
                        final[cogname] = []
                    final[cogname].append(cmd)
        return final

    @commands.command(hidden=True)
    async def help(self, ctx, lookup=None, type=None):
        """
        Shows help for given command or
        lists all/category commands
        <examples>
        <cmd></cmd>
        <res>Sends an embed listing all commands</res>
        <cmd>money</cmd>
        <res>Sends help and info for command *money*</res>
        <cmd>Conversion</cmd>
        <res>Lists all commands in the *Conversion* category</res>
        <cmd>Hypixel cog</cmd>
        <res>Lists all commands in the *Hypixel* category</res>
        </examples>
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

        # Look up command or cog
        else:
            cmd = self.bot.get_command(lookup.lower())
            if cmd and type != 'cog':
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
                                examples += f'`> {ctx.prefix}{cmd.name} {line[2:]}`\n'
                            else:
                                examples += line + '\n'
                    cmd_help = final_help
                    examples = examples[:-1]
                        
                embed = discord.Embed(
                    title=cmd.name,
                    description=cmd_help,
                    colour=0x87ef73
                    )
                embed.add_field(name='Syntax', value=f'`{ctx.prefix}{cmd.name} {cmd.signature}`')
                if cmd.aliases:
                    embed.add_field(name='Aliases', value=' '.join(map(lambda x: f'`{x}`', cmd.aliases)))
                if isinstance(cmd, commands.Group):
                    embed.add_field(name='Subcommands', value=' '.join(f'`{i.name}`' for i in cmd.commands))
                if examples:
                    embed.add_field(name='Examples', value=examples, inline=False)
                await ctx.send(embed=embed)
            else:
                # Look for cog
                cog = self.bot.get_cog(lookup)
                if cog != None:
                    cog = list(filter(lambda x: not x.hidden,cog.get_commands()))

                if cog == None or len(cog) == 0:
                    await ctx.send('No command or cog found with that name')
                    return

                cog.sort(key=lambda c: not bool(c.help))

                final = ''
                for cmd in cog:
                    final += f'**{cmd.name}**' + (f' - {cmd.short_doc}' if cmd.short_doc else '') + '\n'
                embed = discord.Embed(title=lookup,description=final,colour=0x3498db)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CustomHelp(bot))