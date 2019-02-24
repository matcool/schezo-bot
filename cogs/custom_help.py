from discord.ext import commands
import discord

class customHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def commands_dict(self):
        final = {}
        for cogname, cog in self.bot.cogs.items():
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    if final.get(cogname) == None:
                        final[cogname] = []
                    final[cogname].append(cmd)
        return final

    @commands.command(hidden=True)
    async def help(self,ctx,lookup=None,type=None):
        # Show all cogs and their commands WITHOUT short doc
        if lookup is None:
            cmds = self.commands_dict()

            # Sort by name
            for k in cmds:
                cmds[k].sort(key = lambda c: c.name)

            embed = discord.Embed(colour=0x3498db)
            for cog in cmds:
                final = ""
                for cmd in cmds[cog]:
                    final += f"`{cmd.name}` "
                embed.add_field(name=cog, value=final, inline=False)
            await ctx.send(embed=embed)

        # Look up command or cog
        else:
            cmd = self.bot.get_command(lookup)
            if cmd and type != 'cog':
                if cmd.help:
                    embed = discord.Embed(
                        title=cmd.name.capitalize(),
                        description=cmd.help,
                        colour=0xd0d0d0
                        )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('No help found for that command (blame mat)')
                    return
            else:
                cog = self.bot.get_cog(lookup)
                if cog != None:
                    cog = list(filter(lambda x: not x.hidden,cog.get_commands()))

                if cog == None or len(cog) == 0:
                    await ctx.send('No command or cog found with that name')
                    return

                cog.sort(key = lambda c: not bool(c.help))

                final = ""
                for cmd in cog:
                    final += f"**{cmd.name}**" + (f" - {cmd.short_doc}" if cmd.short_doc else "") + "\n"
                embed = discord.Embed(title=lookup,description=final,colour=0x3498db)
                await ctx.send(embed=embed)





                

def setup(bot):
    bot.add_cog(customHelp(bot))