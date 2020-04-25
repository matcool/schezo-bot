import discord
from discord.ext import commands, buttons
import pendulum
import aiohttp
import math

class RateLimited(Exception):
    pass

class Money(commands.Cog, name='Conversion_'):
    __slots__ = 'bot', 'api_key', 'currencies', 'base', 'currency_rates', 'update_time', 'max_requests'
    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.bot.config.get('currencyapikey')
        if self.api_key is None:
            raise Exception('No currency api key found')
            self.bot.remove_cog('Money')
            return
        self.currencies = None
        # Currency rates are stored with the structure of:
        # {
        #   "NAME": (value, timestamp)
        # }
        # where value is how much of that currency is 1 euro (aka the base currency)
        self.base = 'EUR'
        self.currency_rates = {}
        # update every 2 hours
        self.update_time = 2 * 3600
        self.max_requests = 90

    def needs_update(self, t):
        now = pendulum.now('UTC').timestamp()
        return now - t > self.update_time

    async def convert_currency(self, session, a, b, amt=1):
        """Converts currency a to b (with optional amount)"""
        usage = await self.get_usage(session)
        if usage > self.max_requests - 2: raise RateLimited('Rate limited')
        
        aa = self.currency_rates.get(a)
        if aa is None or self.needs_update(aa[1]):
            await self.update_currency(session, a)
        
        bb = self.currency_rates.get(b)
        if bb is None or self.needs_update(bb[1]):
            await self.update_currency(session, b)

        a = self.currency_rates[a][0]
        b = self.currency_rates[b][0]
        return (b / a) * amt

    async def update_currencies(self, session):
        async with session.get(f'https://free.currconv.com/api/v7/currencies?apiKey={self.api_key}') as r:
            js = await r.json()
            self.currencies = js['results']

    async def update_currency(self, session, currency):
        async with session.get(f'https://free.currconv.com/api/v7/convert?apiKey=&q={self.base}_{currency}&compact=ultra&apiKey={self.api_key}') as r:
            js = await r.json()
            self.currency_rates[currency] = (js[f'{self.base}_{currency}'], pendulum.now('UTC').timestamp())

    async def get_usage(self, session):
        async with session.get(f'https://free.currconv.com/others/usage?apiKey={self.api_key}') as r:
            js = await r.json()
            return js['usage']

    async def curr_info(self, currency):
        if self.currencies is None: await self.update_currencies()
        return self.currencies.get(currency)

    @commands.command()
    async def money(self, ctx, curr_a=None, curr_b=None, amount: float=1):
        """Shows info about currency/currencies and can also convert between currencies"""
        async with aiohttp.ClientSession() as session:
            if self.currencies is None:
                await self.update_currencies(session)

            curr_a = curr_a.upper() if curr_a else None
            curr_b = curr_b.upper() if curr_b else None
            
            # Send all currencies if none are given
            if curr_a is None:
                currencies = list(self.currencies.keys())
                currencies.sort()
                formatted = []
                for curr in currencies:
                    c = self.currencies[curr]
                    # Format so its like "USD - United States Dollar"
                    formatted.append(f"{curr} - {c['currencyName']}")
                
                curr_per_page = 30
                pages = []
                while len(formatted):
                    msg = ''
                    for _ in range(curr_per_page):
                        if len(formatted) == 0: break
                        msg += formatted[0]+'\n'
                        formatted.pop(0)
                    pages.append(msg)
                
                pag = buttons.Paginator(title='List of available currencies', colour=0x8BF488, embed=True, timeout=30, use_defaults=True,
                    entries=pages, length=1, format='```')
                await pag.start(ctx)

            # Send info about currency if only one is given
            elif curr_b is None:
                info = await self.curr_info(curr_a)
                if info is None:
                    return await ctx.send('Unknown currency')
                name = info['currencyName']
                symbol = info.get('currencySymbol')
                symbol = ' - ' + symbol if symbol else ''
                await ctx.send(name + symbol)

            # Convert from one currency to another if both given
            else:
                if self.currencies.get(curr_a) is None or self.currencies.get(curr_b) is None:
                    return await ctx.send('Unknown currency')
                if amount <= 0 or not math.isfinite(amount):
                    return await ctx.send('Invalid amount')
                try:
                    val = await self.convert_currency(session, curr_a, curr_b, amt=amount)
                except RateLimited as e:
                    await ctx.send('Rate limited')
                else:
                    await ctx.send(f'{amount:.2f} {curr_a} is about {val:.2f} {curr_b}')

def setup(bot):
    bot.add_cog(Money(bot))