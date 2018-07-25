from discord.ext import commands
import discord
import asyncio
import random
from mcstatus import MinecraftServer
import aiohttp

class privateCommands:
    def __init__(self, bot):
        self.bot = bot

    #lalal
    snakeBool = False
        
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
        txt = open("../gen/self.bot_memberlist.txt","w+",encoding="utf-8")
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
        txt = open("../gen/self.bot_rolelist.txt","w+",encoding="utf-8")
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
        txt = open("../gen/self.bot_channellist.txt","w+",encoding="utf-8")
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
    async def gamething(self,ctx):
        if self.snakeBool:
            await ctx.send('Someone is playing this already')
            return
        self.snakeBool = True
        w = 10
        h = 15
        score = 0
        snake = [[0,4]]
        food = [6,6]
        KEY_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT = 0,1,2,3
        key = KEY_DOWN
        prevKey = key
        grid = eval('['+(('['+('0,'*h)[:-1]+'],')*w)[:-1]+']')
        msg = await ctx.send('hello')
        scor = await ctx.send('info')
        arrows = ('\N{Black Left-Pointing Triangle}','\N{Up-Pointing Small Red Triangle}','\N{Down-Pointing Small Red Triangle}','\N{Black Right-Pointing Triangle}','\N{Black Square for Stop}')
        for i in arrows: await msg.add_reaction(i)
        
        async def show():
            f = ''
            for y in range(h):
                c = ''
                for x in range(w):
                    if grid[x][y] == 1: c += '\N{Nauseated Face}'
                    elif grid[x][y] == 2: c += '\N{Red Apple}'
                    elif grid[x][y] == 3: c += arrows[key]
                    else: 
                        #c += '\N{Medium White Circle}' 
                        c += '\N{White Large Square}'
                c += '\n'
                f += c
            f += '\n'
            await msg.edit(content=f)
            
        def point(x,y,p):
            grid[x][y] = p
        point(food[0], food[1], 2)   
        frameC = 0
        inputFrameC = 0
        #idleframes = 0
        diemsg = 'GAME OVER'
        while True:
            reamsg = await ctx.get_message(msg.id)
            reas = reamsg.reactions
            for r in reas:
                if r.count > 1:
                    users = await r.users().flatten()
                    if ctx.author in users and r.emoji in arrows:
                        await msg.remove_reaction(r.emoji,ctx.author)
                        key = arrows.index(r.emoji)
                        break
            if key == 4:
                diemsg = 'lol bye'
                break
            if frameC % 5 == 0:
                snake.insert(0, [snake[0][0] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1), snake[0][1] + (key == KEY_UP and -1) + (key == KEY_DOWN and 1)])
                if snake[0][0] == -1: snake[0][0] = w-1
                if snake[0][1] == -1: snake[0][1] = h-1
                if snake[0][0] == w: snake[0][0] = 0
                if snake[0][1] == h: snake[0][1] = 0
                if snake[0] in snake[1:]: break
                if snake[0] == food:
                    food = []
                    score += 1
                    while food == []:
                        food = [random.randint(1, w-2), random.randint(1, h-2)]
                        if food in snake: food = []
                    point(food[0], food[1], 2)
                else:    
                    last = snake.pop()
                    point(last[0], last[1], 0)
                point(snake[0][0], snake[0][1], 1)
                await show()
                infoo = 'last key : '+arrows[key]+'\n'
                infoo += 'score : '+str(score)
                infoo += '\ninputframeC '+str(inputFrameC)
                infoo += '\nprevkey :'+arrows[prevKey]
                await scor.edit(content=infoo)
                if key == prevKey: inputFrameC += 1
                else: inputFrameC = 0

            await asyncio.sleep(1/30)
            frameC += 1
            prevKey = key

            if inputFrameC > h + (w/2):
                diemsg = 'too much time idle'
                break
        await msg.edit(content=diemsg+'\n    Score:'+str(score))
        await scor.delete()
        await msg.clear_reactions()
        self.snakeBool = False

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
    async def sserverpic(self,ctx,*,Id=None):
        if ctx.guild == None: return
        if Id == None: g = ctx.guild
        else: g = self.bot.get_guild(int(Id))
        url = g.icon_url_as(format='png')
        await ctx.send(url)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self,ctx):
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def getemoji(self,ctx,n):
        for i in self.bot.emojis:
            if i.name == n:
                await ctx.send(i)
                return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def mycommand(self,ctx):
        await ctx.send(self.bot.emojis[0])


    @commands.command(hidden=True)
    @commands.check(lambda x: x.message.channel.id in (418209286905135107,418245919872516096,418213017847857160))
    async def dhlcra(self,ctx):
        """shows server info for the unofficial dhlcra 5"""
        serverip = "64.52.84.242"
        server = MinecraftServer(serverip)
        query = server.query()
        n_players = query.players.online
        l_players = query.players.names
        # s_players = "- "+"\n- ".join(l_players) if n_players else "No one :("
        # embed = discord.Embed(title="Dhlcra Season 5 *(unofficial)*", colour=discord.Colour(0x339c31))
        # embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/418209286905135107/470307115215618078/server-icon.png")
        # embed.add_field(name="Server IP", value=serverip)
        # embed.add_field(name="Online Players: {}".format(n_players), value=s_players)
        # await ctx.send(embed=embed)
        l_players = ["zNekro" for i in l_players]
        s_players = "- "+"\n- ".join(l_players) if n_players else "zNekro :("
        embed = discord.Embed(title="zNekro 5 *(zNekro)*", colour=discord.Colour(0x339c31))
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/168770585306857472/bf1db0de05c78eae90fdbeb352c390c4.png")
        embed.add_field(name="zNekro", value="zN.ek.ro")
        embed.add_field(name="ZNekro zNekro: zNekro/zNekro", value=s_players)
        await ctx.send(embed=embed)


    @commands.command(hidden=True)
    async def optifine(self,ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://optifine.net/downloads') as r:
                txt = await r.text()
                n = txt.find("OptiFine 1.13")
                if n != -1:
                    await ctx.send("IT OUT!!!")
                else:
                    await ctx.send("not out :(")
            async with session.get('https://optifine.net/home') as r:
                txt = await r.text()
                start = txt.find("Update to Minecraft 1.13")
                end = txt.find("\r\n",start)
                update = txt[start:end]
                update = update.replace("</b>","").replace("</p>","")
                await ctx.send(update)
             

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

    

def setup(bot):
    bot.add_cog(privateCommands(bot))
