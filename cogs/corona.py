from discord.ext import commands
from typing import Dict
from .utils.time import format_date
from .utils.misc import string_distance
import discord
import aiohttp
import time
import pendulum

class CountryInfo:
    __slots__ = ('cases', 'new_cases', 'deaths', 'new_deaths', 'recovered', 'active', 'cpm')

    def __init__(self, data):
        self.cases = data['cases']
        self.new_cases = data['todayCases']
        self.deaths = data['deaths']
        self.new_deaths = data['todayDeaths']
        self.recovered = data['recovered']
        self.active = data['active']
        self.cpm = data['casesPerOneMillion']

class GlobalInfo:
    __slots__ = ('cases', 'deaths', 'recovered', 'updated')

    def __init__(self, data):
        self.cases = data['cases']
        self.deaths = data['deaths']
        self.recovered = data['recovered']
        self.updated = data['updated'] / 1000

class Corona(commands.Cog):
    __slots__ = ('bot', 'all', 'countries', 'last_updated')
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.all: GlobalInfo = None
        self.countries: Dict[str, CountryInfo] = None

        self.last_updated = None
        self.update_time = 5 * 60 # every 5 minutes

    async def update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://corona.lmao.ninja/all') as r:
                self.all = GlobalInfo(await r.json())

            async with session.get('https://corona.lmao.ninja/countries') as r:
                self.countries = {}
                for country in await r.json():
                    self.countries[country['country']] = CountryInfo(country)
        self.last_updated = time.time()

    @commands.command()
    async def corona(self, ctx, *, country=None):
        if self.last_updated is None or time.time() - self.last_updated > self.update_time:
            await self.update()

        if country is None:
            embed = discord.Embed(title='Worldwide coronavirus status')
            embed.description = '[Data source](https://www.worldometers.info/coronavirus/)'
            embed.add_field(name='Cases', value=f'{self.all.cases:,}')
            embed.add_field(name='Deaths', value=f'{self.all.deaths:,}')
            embed.add_field(name='Recovered', value=f'{self.all.recovered:,}')

            embed.set_footer(text=f'Updated on {format_date(pendulum.from_timestamp(self.all.updated))} (UTC)')
            embed.set_thumbnail(url='https://i.imgur.com/ENjogk0.png')

            await ctx.send(embed=embed)
        else:
            if country not in self.countries:
                country = country.lower()
                countries = tuple(sorted(self.countries.keys(), key=lambda x: string_distance(x.lower(), country)))
                country = countries[0]
            data = self.countries[country]

            embed = discord.Embed(title=f"{country}'s coronavirus status")
            embed.add_field(name='Cases', value=f'{data.cases:,} *+{data.new_cases:,} today*')
            embed.add_field(name='Deaths', value=f'{data.deaths:,} *+{data.new_deaths:,} today*')
            embed.add_field(name='Recovered', value=f'{data.recovered:,}')
            embed.add_field(name='Active', value=f'{data.active:,}')

            embed.set_footer(text=f'Updated on {format_date(pendulum.from_timestamp(self.all.updated))} (UTC)')
            embed.set_thumbnail(url='https://i.imgur.com/ENjogk0.png')

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Corona(bot))