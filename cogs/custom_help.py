from discord.ext import commands
import discord

class customHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def help(self,ctx,cmdOrCog=None,type=None):
        # Show all cogs and their commands WITHOUT short doc
        if cmdOrCog is None:
            cmds = {}
            for cmd in self.bot.commands:
                if not cmd.hidden:
                    if cmds.get(cmd.cog_name) is None:
                        cmds[cmd.cog_name] = []
                    cmds[cmd.cog_name].append(cmd)

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
            cmd = self.bot.get_command(cmdOrCog)
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
                cmds = {}
                for cmd in self.bot.commands:
                    if not cmd.hidden:
                        if cmds.get(cmd.cog_name) is None:
                            cmds[cmd.cog_name] = []
                        cmds[cmd.cog_name].append(cmd)

                if cmds.get(cmdOrCog) is None:
                    await ctx.send('No command or category found with that name')

                for k in cmds:
                    cmds[k].sort(key = lambda c: not bool(c.help))

                else:
                    final = ""
                    for cmd in cmds[cmdOrCog]:
                        final += f"**{cmd.name}**" + (f" - {cmd.short_doc}" if cmd.short_doc else "") + "\n"
                    embed = discord.Embed(title=cmdOrCog,description=final,colour=0x3498db)
                    await ctx.send(embed=embed)





                

def setup(bot):
    bot.add_cog(customHelp(bot))