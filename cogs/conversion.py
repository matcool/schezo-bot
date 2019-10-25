from discord.ext import commands
import re

class Conversion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.feet_regex = re.compile('(?:([\\d\\.]+)\')?(?:([\\d\\.]+)\"?)?')

    @commands.command()
    async def celsius(self, ctx, tmp_fahrenheit: float):
        """Converts from fahrenheit to celsius"""
        await ctx.send("{}°C".format(round(5 * (tmp_fahrenheit - 32) / 9, 1)))

    @commands.command(aliases=[
        'farenheit', 'farenreit', 'fárenrráite', 'fárenrráiti', 'fareraide', 'фаренхайт', 'fahrehnheit', 'farenheight', 'americancelsius', 'americantemperatureunits', '华氏度', 'farenright'
    ])
    async def fahrenheit(self, ctx, tmp_celsius: float):
        """Converts from celsius to fahrenheit"""
        await ctx.send("{}°F".format(round((9 * tmp_celsius / 5) + 32, 1)))

    @commands.command(aliases=['lbs'])
    async def pounds(self, ctx, kg: float):
        """Converts from kilograms to pounds"""
        await ctx.send("{}lb".format(round(kg * 2.204623, 1)))

    @commands.command(aliases=['kg', 'kilogram'])
    async def kilograms(self, ctx, pounds: float):
        """Converts from pounds to kilograms"""
        await ctx.send("{}kg".format(round(pounds * 0.4535924, 1)))

    @commands.command(aliases=['inches', 'inch', 'foot'])
    async def feet(self, ctx, cm: float):
        """
        Converts from cm to inches (and feet)
        <examples>
        <cmd>162.56</cmd>
        <res>5'4"</res>
        </examples>
        """
        if not cm: return await ctx.send('0')
        inches = cm / 2.54
        feet, inches = divmod(inches, 12)
        final = (f"{int(feet)}'" if feet else '') + (f'{inches:.2f}"' if inches else '')
        await ctx.send(final)

    @commands.command(aliases=['centimeter'])
    async def cm(self, ctx, *, feet):
        """
        Converts from imperial to cm
        <examples>
        <cmd>5'4"</cmd>
        <res>162.56cm</res>
        <cmd>5'</cmd>
        <res>152.40cm</res>
        <cmd>4"</cmd>
        <res>10.16cm</res>
        <cmd>4</cmd>
        <res>10.16cm</res>
        </examples>
        """
        match = self.feet_regex.match(feet)
        if not match: return await ctx.send('Invalid')
        feet, inches = map(lambda x: float(x) if x else 0, match.groups())
        inches += feet * 12
        await ctx.send(f'{inches * 2.54:.2f}cm')

def setup(bot):
    bot.add_cog(Conversion(bot))