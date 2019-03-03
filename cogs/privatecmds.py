from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import asyncio
import random
from mcstatus import MinecraftServer
import aiohttp
import psutil

class privateCommands(commands.Cog, name='Private Commands', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command()
    @commands.is_owner()
    async def statusc(self,ctx,*args):
        if len(args) != 0:
            acttype = 0
            if args[0] == "!watching":
                acttype = 3
                args = args[1:]
            act = discord.Activity(name=" ".join(args),type=acttype)
            await self.bot.change_presence(activity=act)

    @commands.command()
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
                

    @commands.command()
    @commands.is_owner()
    async def say(self,ctx, *, string: str):
        await ctx.send(string)

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
    @commands.is_owner()
    async def burn(self,ctx):
        await self.bot.change_presence(activity=discord.Activity(name="the world burn",type=discord.ActivityType.watching))

    @commands.command()
    @commands.is_owner()
    async def nickname(self,ctx,*,nickname):
        me = ctx.guild.me
        await me.edit(nick=nickname)

    @commands.command()
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

    @commands.command()
    @commands.is_owner()
    async def kill(self,ctx):
        await self.bot.logout()

    def sync_dhlcra(self,serverip):
        try:
            server = MinecraftServer(serverip)
            query = server.query(retries=1)
            #status = server.status(retries=1)
        except Exception:
            return False
        n_players = query.players.online
        l_players = query.players.names
        s_players = "- "+"\n- ".join(l_players) if n_players else "No one :("
        return (n_players,l_players,s_players)


    @commands.command(enabled=False)
    @commands.check(lambda x: x.message.channel.id in (418209286905135107,418245919872516096,418213017847857160))
    async def dhlcra(self,ctx):
        """shows server info for the dhlcra 6"""
        #serverip = "64.52.87.37"
        serverip = "0.0.0.0"
        result = await self.bot.loop.run_in_executor(None, self.sync_dhlcra, serverip)
        if not result:
            await ctx.send("Error while trying to connect")
            return
        #serverip = "64.52.87.37"
        serverip = "dhlcra.us.to"
        n_players,l_players,s_players = result
        embed = discord.Embed(title="Dhlcra Season 6", colour=discord.Colour(0x339c31))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/418209286905135107/482244469211791360/dhlcra.png")
        embed.add_field(name="Server IP", value=serverip)
        embed.add_field(name="Online Players: {}".format(n_players), value=s_players)
        await ctx.send(embed=embed)  

    @commands.cooldown(1,5,BucketType.default)
    @commands.command()
    async def matstats(self,ctx):
        gb = 1/(1024 ** 3)
        cpu = int(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        used = "{0:.2f}".format(mem.used*gb)
        total = "{0:.2f}".format(mem.total*gb)
        await ctx.send("CPU Usage: {}%\nRAM Usage: {}G/{}G".format(cpu,used,total))

    @commands.command()
    async def reply(self,ctx,msgId,*,msg):
        msgr = await ctx.get_message(msgId)
        embed = discord.Embed(description=msgr.content)
        embed.set_author(name=msgr.author.display_name,icon_url=msgr.author.avatar_url)
        await ctx.send(msg,embed=embed)

    @commands.command()
    @commands.is_owner()
    async def countthing(self,ctx,limit):
        count = {}
        total = 0
        if limit == 'None':
            limit = None
        else:
            limit = int(limit)
        async for msg in ctx.channel.history(limit=limit):
            name = msg.author.display_name
            if count.get(name) is None:
                count[name] = 0
            count[name] += 1
            total+=1

        percent = list((i,j/total*100) for i,j in count.items())
        percent.sort(key=lambda x: x[1],reverse=True)
        t = '\n'.join("{} has {}%".format(*i) for i in percent)
        print(t)
        await ctx.send(t)

    @commands.command()
    @commands.is_owner()
    async def getlogofself(self,ctx,limit):
        if limit == 'None':
            limit = None
        else:
            limit = int(limit)
        final = ''
        async for msg in ctx.channel.history(limit=limit):
            if msg.author.id == ctx.author.id and len(msg.clean_content) > 0:
                final += msg.clean_content + '\n'

        with open('epiclog.txt','w',encoding='utf-8') as f:
            f.write(final)
        await ctx.send('done')

def setup(bot):
    bot.add_cog(privateCommands(bot))
