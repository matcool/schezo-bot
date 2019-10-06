from discord.ext import commands
import discord
from typing import Tuple, Dict, List
import re

class CustomHelp(commands.Cog):
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

    @staticmethod
    def get_xml_tag(name, string) -> Tuple[str, str]:
        """Finds xml styled tag on given string and returns text inside them, and the string without the tag"""
        open = f'<{name}>'
        close = f'</{name}>'
        start = string.find(open)
        end = string.find(close)
        if start == -1 or end == -1: return
        inside = string[start + len(open) : end]
        string = string[:start] + string[end + len(close):]
        return (inside, string)

    @staticmethod
    def replace_xml_tag(name, string, fmt='{}') -> str:
        """Finds xml styled tag on given string and formats it with given `fmt`"""
        return re.sub(f'(<{name}>)(.*?)(<\/{name}>)', fmt.replace('{}', '\\2'), string)

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
                commands = ' '.join(map(lambda cmd: f'`{cmd.name}`', cmds[cog]))
                embed.add_field(name=cog, value=commands, inline=False)
            await ctx.send(embed=embed)

        # Look up command or cog
        else:
            cmd = self.bot.get_command(lookup.lower())
            if cmd and type != 'cog':
                cmd_help = cmd.help
                examples = None
                if cmd_help:
                    result = self.get_xml_tag('examples', cmd_help)
                    if result:
                        examples, cmd_help = result
                        examples = self.replace_xml_tag('cmd', examples, fmt=f'`> {ctx.prefix}{cmd.name} {{}}`')
                        # unused atm
                        examples = self.replace_xml_tag('res', examples, fmt='{}')
                        
                embed = discord.Embed(
                    title=cmd.name,
                    description=cmd_help,
                    colour=0xd0d0d0
                    )
                embed.add_field(name='Syntax', value=f'`{ctx.prefix}{cmd.name} {cmd.signature}`')
                if cmd.aliases:
                    embed.add_field(name='Aliases', value=' '.join(map(lambda x: f'`{x}`', cmd.aliases)))
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