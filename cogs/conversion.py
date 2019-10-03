from discord.ext import commands

class Conversion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def celsius(self, ctx, temperature: float):
        """Converts from fahrenheit to celsius"""
        await ctx.send("{}°C".format(round(5*(temperature-32)/9,1)))

    @commands.command(aliases=[
        'farenheit', 'farenreit', 'fárenrráite', 'fárenrráiti', 'fareraide', 'фаренхайт', 'fahrehnheit', 'farenheight', 'americancelsius', 'americantemperatureunits', '华氏度', 'farenright'
        ])
    async def fahrenheit(self, ctx, temperature: float):
        """Converts from celsius to fahrenheit"""
        await ctx.send("{}°F".format(round((9*temperature/5)+32,1)))

    @commands.command(aliases=['lbs'])
    async def pounds(self, ctx, kg: float):
        """Converts from kilograms to pounds"""
        await ctx.send("{}lb".format(round(kg * 2.204623,1)))

    @commands.command(aliases=['kg','kilogram'])
    async def kilograms(self, ctx, pounds: float):
        """
        Converts from pounds to kilograms
        <example>
        <cmd>120</cmd>
        <res>54.4kg</res>
        </example>
        """
        await ctx.send("{}kg".format(round(pounds * 0.4535924,1)))

    @commands.command(aliases=['cm'])
    async def metric(self, ctx, *, x):
        """
        Converts from inches (default) to cm
        <example>
        Convert from feet (and inches)
        <cmd>5'4"</cmd>
        <res>162.56cm</res>
        </example>
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
    async def imperial(self, ctx, cm: float):
        """
        Converts from cm to inches (and feet)

        {prefix}imperial 162.56
        = 5'4"
        """
        inches = cm / 2.54
        feet, inches = divmod(inches, 12)
        final = ""
        if feet != 0:
            final += str(int(feet)) + '\''
        final += str(round(inches,2)) + '"'
        await ctx.send(final)

    @commands.command()
    async def mbps(self, ctx, mbs: float):
        """Converts from MB/s to Mbps"""
        await ctx.send('{}Mbps'.format(mbs*8))

    @commands.command()
    async def mbs(self, ctx, mbps: float):
        """Converts from Mbps to MB/s"""
        await ctx.send('{}MB/s'.format(round(mbps/8,1)))

def setup(bot):
    bot.add_cog(Conversion(bot))