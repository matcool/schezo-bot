from discord.ext import commands
import discord
import asyncio
import random

class privateCommands:
    def __init__(self, bot):
        self.bot = bot

    #lalal
    snakeBool = False
        
    @commands.command(hidden=True)
    @commands.is_owner()
    async def statusc(self,ctx,*, string=None):
        if string is None:
            with open('../bot_config.json') as file:
                jsonf = json.load(file)
                gamename = jsonf['game']
            await self.bot.change_presence(activity=discord.Game(gamename.replace('%numberofservers%', str(len(self.bot.guilds)))))
        else:
            await self.bot.change_presence(activity=discord.Game(string))

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
                    else: c += '\N{Medium White Circle}' #'\N{White Large Square}'
                c += '\n'
                f += c
            f += '\n'
            await msg.edit(content=f)
            
        def point(x,y,p):
            grid[x][y] = p
        point(food[0], food[1], 2)   
        frameC = 0
        inputFrameC = 0
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


def setup(bot):
    bot.add_cog(privateCommands(bot))
