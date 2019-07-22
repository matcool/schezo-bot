from discord.ext import commands
from discord.ext import buttons
from discord.ext.commands.cooldowns import BucketType
import aiohttp
import json

class Conversion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('bot_config.json') as file:
            jsonf = json.load(file)
            self.currencyapikey = jsonf['currencyapikey']

    @commands.cooldown(50,3600,BucketType.default)
    @commands.command()
    async def money(self,ctx,curFrom=None,curTo=None,amount=None):
        """
        Converts an amount from one currency to another.

        **Usage**:
        *s.money (x currency) (y currency) [amount]*
        will convert from x amount to y. default amount is 1
        """

        if curFrom: curFrom = curFrom.upper()
        if curTo: curTo = curTo.upper()

        if amount:
            try:
                amount = float(amount)
            except ValueError:
                await ctx.send("Invalid amount.")
                return
        else: amount = 1

        amount = abs(amount)

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://free.currconv.com/api/v7/currencies?apiKey={self.currencyapikey}') as r:
                js = await r.json()
                js = js["results"]
                if curTo == None and curFrom != None and curFrom in js:
                    symbol = js[curFrom].get('currencySymbol')
                    await ctx.send(js[curFrom]["currencyName"]+(' - '+symbol if symbol != None else ''))
                    return

                if curTo == None and curFrom == None:
                    if ctx.guild == None:
                        return await ctx.send('Sorry but this command does not work on DMs (i cant remove your reactions)\nPlease use this in a server')
                    keys = list(js.keys())
                    keys.sort()
                    formatted = []
                    for key in keys:
                        c = js[key]
                        final = f"{key} - {c['currencyName']}"
                        formatted.append(final)
                    
                    nperpage = 30
                    pages = []
                    while len(formatted):
                        msg = ''
                        for _ in range(nperpage):
                            if len(formatted) == 0: break
                            msg += formatted[0]+'\n'
                            formatted.pop(0)
                        pages.append(msg)
                    
                    p = buttons.Paginator(title='List of available currencies', colour=0x8BF488, embed=True, timeout=30, use_defaults=True,
                        entries=pages, length=1, format='```')
                    await p.start(ctx)
                elif curFrom not in js or curTo not in js:
                    await ctx.send('Unknown currency! do `s.money` to see a list of all available ones.')
                    return
                else:
                    async with session.get(f'https://free.currconv.com/api/v7/convert?q={curFrom}_{curTo}&compact=y&apiKey={self.currencyapikey}') as r:
                        js = await r.json()
                        value = float(js[f"{curFrom}_{curTo}"]["val"])*amount

                        await ctx.send("{0} {1} is about {2:.2f} {3}".format(amount,curFrom,value,curTo))

    @commands.command()
    async def celsius(self, ctx, temperature):
        """Converts from fahrenheit to celsius"""
        t = float(temperature)
        await ctx.send("{}°C".format(round(5*(t-32)/9,1)))

    @commands.command()
    async def fahrenheit(self, ctx, temperature):
        """Converts from celsius to fahrenheit"""
        t = float(temperature)
        await ctx.send("{}°F".format(round((9*t/5)+32,1)))

    @commands.command(aliases=['lbs'])
    async def pounds(self, ctx, kg):
        """Converts from kilograms to pounds"""
        t = float(kg) * 2.204623
        await ctx.send("{}lb".format(round(t,1)))

    @commands.command(aliases=['kg','kilogram'])
    async def kilograms(self, ctx, pounds):
        """Converts from pounds to kilograms"""
        t = float(pounds) * 0.4535924
        await ctx.send("{}kg".format(round(t,1)))

    @commands.command(aliases=['cm'])
    async def metric(self, ctx, *, x):
        """
        Converts from inches (default) to cm
        
        Can also convert from feet (and inches) like so:
        s.metric 5'4"
        = 162.56cm
        """
        ft = x.find('\'')
        ic = x.find('"')
        inches = 0
        feet = 0
        if ft == ic == -1:
            inches = float(x)
        else:
            if ic != -1:
                inches = float(x[(ft+1 if ft != -1 else 0):ic])
            if ft != -1:
                feet = float(x[0:ft])
        inches += feet * 12
        await ctx.send("{}cm".format(round(inches*2.54,2)))

    @commands.command(aliases=['inches','feet','inch','foot'])
    async def imperial(self, ctx, cm):
        """
        Converts from cm to inches (and feet)

        s.imperial 162.56
        = 5'4"
        """
        inches = float(cm) / 2.54
        feet, inches = divmod(inches, 12)
        final = ""
        if feet != 0:
            final += str(int(feet)) + '\''
        final += str(round(inches,2)) + '"'
        await ctx.send(final)

    @commands.command()
    async def mbps(self, ctx, mbs):
        """Converts from MB/s to Mbps"""
        await ctx.send('{}Mbps'.format(float(mbs)*8))

    @commands.command()
    async def mbs(self, ctx, mbps):
        """Converts from Mbps to MB/s"""
        await ctx.send('{}MB/s'.format(round(float(mbps)/8,1)))


def setup(bot):
    bot.add_cog(Conversion(bot))