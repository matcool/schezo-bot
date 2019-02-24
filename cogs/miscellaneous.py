from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import random
import calendar
import aiohttp
from bs4 import BeautifulSoup
import re


class Miscellaneous(commands.Cog):
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
    async def invite(self,ctx):
        """Sends this bot invite link."""
        await ctx.send('https://discordapp.com/oauth2/authorize?client_id=317323392992935946&scope=bot&permissions=270400')

    @commands.command()
    async def pfp(self,ctx,user:discord.Member=None):
        """Gets a profile pic from mention (or userid) or from msg author"""
        if user == None: user = ctx.author
        await ctx.send(user.avatar_url_as(format="png"))

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
        await ctx.send("".join(list(map(lambda x: x if random.random() < 0.5 else x.upper(),msg.lower()))))

    @commands.command()
    async def scramble(self,ctx,*,msg):
        """Scramble the given message"""
        await ctx.send("".join(sorted(list(msg),key = lambda x: random.random())))
    
    @commands.command()
    async def joinedat(self,ctx,user:discord.Member=None):
        """Says when you (or mentioned) joined the server"""
        if user == None: user = ctx.author
        a = user.joined_at
        await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))

    @commands.command()
    async def createdat(self,ctx,user:discord.Member=None):
        """Says when you (or mentioned) created your discord account"""
        if user == None: user = ctx.author
        a = user.created_at
        await ctx.send("{0} {1.day} {1.year}".format(calendar.month_name[a.month], a))

    @commands.cooldown(5,600,BucketType.default)
    @commands.command()
    async def optifine(self,ctx,version):
        """Get OptiFine download links for given version"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://optifine.net/downloads') as r:
                rawhtml = await r.read()
        
        bs = BeautifulSoup(rawhtml,features="html.parser")
        maxversions = 3
        if version != 'all':
            tmp = bs.find(text='Minecraft '+version)
            if tmp is None:
                tmp = bs.find(text=re.compile(version+' '))
                if tmp is None:
                    await ctx.send("No OptiFine found for that verison.")
                    return
                else:
                    embed = discord.Embed(title='Only one OptiFine found for that version')
                    embed.add_field(name=tmp.string,value=tmp.findNext(class_='downloadLineDownload').a.get('href'),inline=True)
                    await ctx.send(embed=embed)
                    return
            tmp = tmp.findNext(class_='downloadTable')
        else:
            tmp = bs

        names = [i.string for i in tmp.findAll('td',class_=re.compile('downloadLineFile'),limit=maxversions)]
        links = [i.a.get('href') for i in tmp.findAll('td',class_='downloadLineMirror',limit=maxversions)]

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