from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import aiohttp


class Conversion:
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command()
    async def celsius(self, ctx, temperature):
        """Converts from fahrenheit to celsius"""
        t = float(temperature)
        await ctx.send("{}°C".format(round(5*(t-32)/9,1)))

    @commands.command()
    async def fahrenheit(self, ctx, temperature):
        """Converts from celsius to fahrenheit"""
        t = float(temperature)
        await ctx.send("{}°F".format(round(9*(t+32)/5,1)))

def setup(bot):
    bot.add_cog(Conversion(bot))