from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import random
import calendar
import aiohttp
from bs4 import BeautifulSoup
import re


class Miscellaneous:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embed(self,ctx,title,content,color):
        """Makes a embed message with the args given."""
        embed = discord.Embed(title=title, description=content, colour=int(color, 16))
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self,ctx):
        """Tests the bot latency"""
        await ctx.send(str(int(self.bot.latency*1000))+"ms")

    @commands.command()
    async def spacefy(self,ctx,*, string: str):
        """a e s t h e t i c 'fy the given string."""
        await ctx.send(" ".join(string))

    @commands.command()
    async def invite(self,ctx):
        """Sends this bot invite link."""
        part1 = 'https://discordapp.com/oauth2/authorize?'
        part2 = 'client_id=317323392992935946&scope=bot&permissions=270400'
        await ctx.send(part1+part2)


    @commands.command()
    async def pfp(self,ctx,uid=None):
        """Gets a profile pic from id or from msg author"""
        if uid is None:
            await ctx.send(ctx.message.author.avatar_url_as(format="png"))
        else:
            m = self.bot.get_user(int(uid))
            await ctx.send(m.avatar_url_as(format="png"))

    @commands.command()
    async def serverpic(self,ctx,*,Id=None):
        """Sends pic of server icon"""
        if not ctx.guild and not Id: return
        if Id == None: g = ctx.guild
        else: g = self.bot.get_guild(int(Id))
        url = g.icon_url_as(format='png')
        await ctx.send(url)

    @commands.command()
    async def mock(self,ctx,*,msg):
        """dOeS thIS To yOuR meSsaGE"""
        await ctx.send(""+"".join(list(map(lambda x: x if random.random() < 0.5 else x.upper(),msg.lower()))))

    @commands.command()
    async def scramble(self,ctx,*,msg):
        """Scramble the given word"""
        await ctx.send(""+"".join(sorted(list(msg),key = lambda x: random.random())))
    
    @commands.command()
    async def joinedat(self,ctx):
        """Says when you joined the server"""
        a = ctx.message.author.joined_at
        await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))

    @commands.command()
    async def createdat(self,ctx):
        """Says when you created your discord account"""
        a = ctx.message.author.created_at
        await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))

    @commands.cooldown(50,3600,BucketType.default)
    @commands.command()
    async def money(self,ctx,curFrom,curTo=None,amount=None):
        """
        Converts an amount from one currency to another.

        **Usage**:
        *mb!money (x currency) (y currency) [amount]*
        will convert from x amount to y. default amount is 1
        """

        curFrom = curFrom.upper()
        if curTo:
            curTo = curTo.upper()

        if amount:
            try:
                amount = float(amount)
            except ValueError:
                await ctx.send("Invalid amount.")
                return
        else: amount = 1

        amount = abs(amount)

        async with aiohttp.ClientSession() as session:
            async with session.get('https://free.currencyconverterapi.com/api/v6/currencies') as r:
                js = await r.json()
                js = js["results"]
                if not curTo and curFrom in js:
                    await ctx.send(js[curFrom]["currencyName"])
                    return
                if curTo:
                    if curFrom not in js or curTo not in js:
                        await ctx.send("List of all avaliable currencies :```{}```".format(" ".join([i for i in js])))
                        return
            async with session.get(f'https://free.currencyconverterapi.com/api/v6/convert?q={curFrom}_{curTo}&compact=y') as r:
                js = await r.json()
                value = float(js[f"{curFrom}_{curTo}"]["val"])*amount

                await ctx.send("{0} {1} is about {2:.2f} {3}".format(amount,curFrom,value,curTo))

    @commands.cooldown(5,600,BucketType.default)
    @commands.command()
    async def optifine(self,ctx,version):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://optifine.net/downloads') as r:
                rawhtml = await r.read()
        
        bs = BeautifulSoup(rawhtml,features="html.parser")
        tmp = bs.find(text="Minecraft "+version)
        if tmp is None:
            tmp = bs.find(text=re.compile(version))
            if tmp is None:
                await ctx.send("No OptiFine found for that verison.")
                return
            else:
                link = tmp.parent.nextSibling.nextSibling.nextSibling.nextSibling.a.get('href')
                embed = discord.Embed(title='Only one OptiFine found for that version')
                embed.add_field(name=tmp,value=link,inline=True)
                await ctx.send(embed=embed)
                return

        tmp = tmp.parent.nextSibling.nextSibling.nextSibling.nextSibling

        maxversions = 3

        names = [i.string for i in tmp.find_all('td',class_=re.compile('downloadLineFile'),limit=maxversions)]
        links = [i.a.get('href') for i in tmp.find_all('td',class_='downloadLineMirror',limit=maxversions)]

        embed = discord.Embed(title='Optifine '+version)
        for name,link in zip(names,links):
            embed.add_field(name=name,value=link,inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def rate(self,ctx,*,ratee):
        """rates something"""
        total = sum([ord(i) for i in ratee])
        rnd = random.Random(total)
        await ctx.send("I'd give {} a {}/10".format(ratee,rnd.randint(0,10)))


         



def setup(bot):
    bot.add_cog(Miscellaneous(bot))