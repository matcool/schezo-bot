from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import asyncio
import random
from mcstatus import MinecraftServer
import aiohttp
import psutil

class privateCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self,ctx):
        cmds = {}
        for cmd in self.bot.commands:
            if not cmds.get(cmd.cog_name):
                cmds[cmd.cog_name] = []
            if not cmd.hidden:
                cmds[cmd.cog_name].append(cmd)
        cmds = {key: value for key, value in cmds.items() if value != []}
        embed = discord.Embed(title="Matbot help",colour=int("f0f0f0", 16))
        for cog in cmds:
            final = ""
            hadHelp = True
            for cmd in cmds[cog]:
                if not hadHelp:
                    final = final[0:len(final)-1] + " "
                final += f"**{cmd.name}**" + (f" - {cmd.help}" if cmd.help else "") + "\n"
                hadHelp = bool(cmd.help)
            embed.add_field(name=cog, value=final, inline=True)
        await ctx.send(embed=embed)
       
    @commands.command(hidden=True)
    @commands.is_owner()
    async def statusc(self,ctx,*args):
        if len(args) != 0:
            acttype = 0
            if args[0] == "!watching":
                acttype = 3
                args = args[1:]
            act = discord.Activity(name=" ".join(args),type=acttype)
            await self.bot.change_presence(activity=act)


    @commands.command(hidden=True)
    @commands.is_owner()
    async def sendemojis(self,ctx):
        emojis = self.bot.emojis
        msgs = []
        current = 0
        for i in range(len(emojis)):
            if len(msgs) < current + 1:
                msgs.append("")
            if len(msgs[current]) < 2000 and len(str(emojis[i - 1])) < 2000 - len(msgs[current]):
                msgs[current] += str(emojis[i - 1])
            else:
                msgs.append("")
                current += 1
                msgs[current] += str(emojis[i - 1])
        for msg in msgs:
            await ctx.send(msg)
            await asyncio.sleep(2)
                

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say(self,ctx, *, string: str):
        await ctx.send(string)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def scrolltext(self,ctx,*, string="text"):
        """dhl dhld hldmade thx"""
        string = "          "+string+"          "
        idk = 0
        msg = await ctx.send("`>|"+string[idk:idk+10]+"|<`")
        while idk+10 < len(string):
            idk += 1
            furry = "`>|{}|<`".format(string[idk:idk+10])
            await msg.edit(content=furry)
            await asyncio.sleep(0.9)
        await msg.add_reaction('\U00002705')
        #thx dhl <3

    @commands.command(hidden=True)
    @commands.is_owner()
    async def hiddencommands(self,ctx):
        c = self.bot.commands
        h = []
        for i in c:
            if i.hidden and i.name != "hiddencommands":
                h.append(i)
        f = "```"
        for i in h:
            f += "{0.name} {0.description}\n".format(i)
            
        f = f[:-1]
        f += "```"

        await ctx.send(f)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def botservers(self,ctx):
        g = self.bot.guilds
        h = []
        for i in g:
            h.append(i.name)
        f = "```"
        for i in h:
            f += i+"\n"
        f = f[:-1]
        f += "```"
        await ctx.send(f)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def memberlist(self,ctx):
        txt = open("gen/bot_memberlist.txt","w+",encoding="utf-8")
        f = ""
        for m in ctx.message.guild.members:
            f += m.display_name
            if m.nick != None:
                f += " - "+m.name
            f += " >> "+m.roles[len(m.roles)-1].name
            f += "\n"
        f = f[:-1]
        txt.write(f)
        txt.close()
        await ctx.send("done lol")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def rolelist(self,ctx):
        txt = open("gen/bot_rolelist.txt","w+",encoding="utf-8")
        rs = ""
        for r in ctx.message.guild.role_hierarchy:
            rs += "{0.name}\n".format(r)
        rs = rs[:-1]
        txt.write(rs)
        txt.close()
        await ctx.send("done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def channellist(self,ctx):
        txt = open("gen/bot_channellist.txt","w+",encoding="utf-8")
        f = ""
        fnone = "No category ->\n"
        lastc = None
        for i in ctx.message.guild.text_channels:
            if i.category != None:
                if i.category.name != lastc:
                    lastc = i.category.name
                    f += "\n"+i.category.name+" ->\n"
                f += "#"+i.name+"\n"
            else:
                fnone += "#"+i.name+"\n"
        f = f[1:]
        f += "\n"+fnone[:-1]
        txt.write(f)
        txt.close()
        await ctx.send("done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def burn(self,ctx):
        await self.bot.change_presence(activity=discord.Activity(name="the world burn",type=discord.ActivityType.watching))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reactmsg(self,ctx,msgid,emoji):
        emo = re.findall(r"<:.+:([0-9]+)>",emoji)
        msgtor = await ctx.get_message(int(msgid))
        if emo != []:
            await msgtor.add_reaction(self.bot.get_emoji(int(emo[0])))
        else:
            await msgtor.add_reaction(emoji)
        await ctx.message.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def nickname(self,ctx,*,nickname):
        me = ctx.guild.me
        await me.edit(nick=nickname)

    @commands.command(hidden=True)
    async def spacename(self,ctx,*,name):
        if not ctx.guild: return
        mem = ctx.author
        gperms = mem.guild_permissions
        cperms = mem.permissions_in(ctx.channel)
        if gperms.manage_channels or cperms.manage_channels:
            c = ctx.channel
            await c.edit(name=name.replace(" ",chr(0x2005)),reason="space cool")
            await ctx.send("done")
        else:
            return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self,ctx):
        await self.bot.close()

    @commands.command(hidden=True)
    #@commands.is_owner()
    async def getemoji(self,ctx,n):
        for i in self.bot.emojis:
            if i.name == n:
                await ctx.send(i)
                return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def mycommand(self,ctx):
        await ctx.send(self.bot.emojis[0])


    def sync_dhlcra(self,serverip):
        try:
            server = MinecraftServer(serverip)
            query = server.query(retries=1)
        except Exception:
            return False
        n_players = query.players.online
        l_players = query.players.names
        s_players = "- "+"\n- ".join(l_players) if n_players else "No one :("
        return (n_players,l_players,s_players)


    @commands.command(hidden=True)
    @commands.check(lambda x: x.message.channel.id in (418209286905135107,418245919872516096,418213017847857160))
    async def dhlcra(self,ctx):
        """shows server info for the unofficial dhlcra 5"""
        serverip = "64.52.87.37"
        result = await self.bot.loop.run_in_executor(None, self.sync_dhlcra, serverip)
        if not result:
            await ctx.send("Error while trying to connect")
            return
        n_players,l_players,s_players = result
        embed = discord.Embed(title="Dhlcra Season 5 *(unofficial)*", colour=discord.Colour(0x339c31))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/418209286905135107/470307115215618078/server-icon.png")
        embed.add_field(name="Server IP", value=serverip)
        embed.add_field(name="Online Players: {}".format(n_players), value=s_players)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def optifine(self,ctx):
        await ctx.send("IT OUT!!! (preview tho but who cares)\n"+"https://optifine.net/adloadx?f=preview_OptiFine_1.13_HD_U_E3_alpha8.jar")
             

    @commands.command(hidden=True)
    async def bigdiki(self,ctx):
        gen = random.Random()
        gen.seed(ctx.author.id+16)
        size = gen.randint(1,10)
        pp = "8{}D".format("="*size)
        # mat's id
        if ctx.author.id == 191233808601841665:
            pp = "8D"
        await ctx.send(pp)

    @commands.cooldown(1,5,BucketType.default)
    @commands.command(hidden=True)
    async def matstats(self,ctx):
        gb = 1/(1024 ** 3)
        cpu = int(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        used = "{0:.2f}".format(mem.used*gb)
        total = "{0:.2f}".format(mem.total*gb)
        await ctx.send("CPU Usage: {}%\nRAM Usage: {}G/{}G".format(cpu,used,total))

    @commands.cooldown(50,3600,BucketType.default)
    @commands.command(hidden=True)
    async def dollar(self,ctx):
        # https://free.currencyconverterapi.com/api/v6/convert?q=USD_BRL&compact=y
        async with aiohttp.ClientSession() as session:
            async with session.get('https://free.currencyconverterapi.com/api/v6/convert?q=USD_BRL&compact=y') as r:
                js = await r.json()
                await ctx.send(js["USD_BRL"]["val"])



    

def setup(bot):
    bot.add_cog(privateCommands(bot))
