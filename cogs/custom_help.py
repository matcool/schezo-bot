from discord.ext import commands
import discord

class customHelp:
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    @commands.command()
    async def help(self,ctx,cmd=None):
        if not cmd:
            cmds = {}
            for cmd in self.bot.commands:
                if not cmd.hidden and cmd.name != 'help':
                    if cmds.get(cmd.cog_name) is None:
                        cmds[cmd.cog_name] = []
                    cmds[cmd.cog_name].append(cmd)

            # Sort whether the command has a help string or not
            for k in cmds:
                cmds[k].sort(key = lambda c: not bool(c.help))

            embed = discord.Embed(title="Matbot help",colour=0x36393F)
            for cog in cmds:
                final = ""
                hadHelp = True
                for cmd in cmds[cog]:
                    if not hadHelp:
                        # replace last char with space
                        final = final[:-1] + " "
                    final += f"**{cmd.name}**" + (f" - {cmd.short_doc}" if cmd.short_doc else "") + "\n"
                    hadHelp = bool(cmd.help)
                embed.add_field(name=cog, value=final, inline=True)
            await ctx.send(embed=embed)
        else:
            cmd = self.bot.get_command(cmd)
            if cmd:
                if cmd.help:
                    embed = discord.Embed(
                        title=f"{cmd.name.capitalize()} help",
                        description=cmd.help,
                        colour=int("d0d0d0", 16)
                        )
                    await ctx.send(embed=embed)
                else:
                    return
            else:
                await ctx.send("Command not found.")

def setup(bot):
    bot.add_cog(customHelp(bot))