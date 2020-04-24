from discord.ext import commands
import re
import math

class Conversion(commands.Cog):
    __slots__ = 'bot', 'feet_regex'
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.feet_regex = re.compile('^(?:(\d+?(?:\.\d+?)?)\'?)?(?:(\d+?(?:\.\d+?)?)\"?)?$')

    @commands.command()
    async def celsius(self, ctx, tmp_fahrenheit: float):
        """Converts from fahrenheit to celsius"""
        if not math.isfinite(tmp_fahrenheit): return await ctx.send('Invalid amount')
        await ctx.send("{}°C".format(round(5 * (tmp_fahrenheit - 32) / 9, 1)))

    @commands.command(aliases=[
        'farenheit', 'farenreit', 'fárenrráite', 'fárenrráiti', 'fareraide', 'фаренхайт', 'fahrehnheit', 'farenheight', 'americancelsius', 'americantemperatureunits', '华氏度', 'farenright'
    ])
    async def fahrenheit(self, ctx, tmp_celsius: float):
        """Converts from celsius to fahrenheit"""
        if not math.isfinite(tmp_celsius): return await ctx.send('Invalid amount')
        await ctx.send("{}°F".format(round((9 * tmp_celsius / 5) + 32, 1)))

    @commands.command(aliases=['lbs'])
    async def pounds(self, ctx, kg: float):
        """Converts from kilograms to pounds"""
        if not math.isfinite(kg): return await ctx.send('Invalid amount')
        await ctx.send("{}lb".format(round(kg * 2.204623, 1)))

    @commands.command(aliases=['kg', 'kilogram'])
    async def kilograms(self, ctx, pounds: float):
        """Converts from pounds to kilograms"""
        if not math.isfinite(pounds): return await ctx.send('Invalid amount')
        await ctx.send("{}kg".format(round(pounds * 0.4535924, 1)))

    @commands.command(aliases=['inches', 'inch', 'foot'])
    async def feet(self, ctx, cm: float):
        """
        Converts from cm to inches (and feet)
        Examples::
        > 162.56
        5'4"
        """
        if cm == 0: return await ctx.send('0')
        if not math.isfinite(cm): return await ctx.send('Invalid amount')
        inches = cm / 2.54
        feet, inches = divmod(inches, 12)
        final = (f"{int(feet)}'" if feet else '') + (f'{inches:.2f}"' if inches else '')
        await ctx.send(final)

    @commands.command(aliases=['centimeter'])
    async def cm(self, ctx, *, feet):
        """
        Converts from imperial to cm
        Examples::
        > 5'4
        162.56cm
        > 5
        152.40cm
        > 4
        10.16cm
        """
        match = self.feet_regex.match(feet)
        if not match or not any(match.groups()):
            return await ctx.send('Invalid amount')
        
        feet, inches = map(lambda x: float(x) if x else 0, match.groups())
        
        if not math.isfinite(feet) or not math.isfinite(inches):
            return await ctx.send('Invalid amount')

        inches += feet * 12
        await ctx.send(f'{inches * 2.54:.2f}cm')

def setup(bot):
    bot.add_cog(Conversion(bot))