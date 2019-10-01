from discord.ext import commands
from discord.ext import buttons
import aiohttp
import json
import pendulum
import math

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('bot_config.json') as file:
            jsonf = json.load(file)
            self.currencyapikey = jsonf['currencyapikey']
        self.base = 'EUR'
        # Stored as (amount, timestamp)
        self.currency_rates = {}
        self.update_time = 2 * 3600
        # ([Currencies], last updated)
        self.currencies = [{}, None]

    def convert_currency(self, a, b, amt=1):
        """Converts currency a to b (with optional amount)"""
        a = self.currency_rates[a][0]
        b = self.currency_rates[b][0]
        return (b / a) * amt

    async def update_currencies(self, session):
        async with session.get(f'https://free.currconv.com/api/v7/currencies?apiKey={self.currencyapikey}') as r:
            js = await r.json()
            self.currencies = (js['results'], pendulum.now().timestamp())

    async def update_currency(self, session, currency):
        async with session.get(f'https://free.currconv.com/api/v7/convert?apiKey=&q={self.base}_{currency}&compact=ultra&apiKey={self.currencyapikey}') as r:
            js = await r.json()
            self.currency_rates[currency] = (js[f'{self.base}_{currency}'], pendulum.now().timestamp())

    async def get_usage(self, session):
        async with session.get(f'https://free.currconv.com/others/usage?apiKey={self.currencyapikey}') as r:
            js = await r.json()
            return js['usage']

    @staticmethod
    def format_time(seconds):
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        pad = lambda x: '0'[len(str(x))-1:]+str(x)
        return f'{pad(minutes)}:{pad(seconds)}'

    @commands.command()
    async def money(self, ctx, curFrom=None, curTo=None, amount=None):
        """
        Converts an amount of one currency to another
        <example>
        <cmd></cmd>
        <res>*Starts paginator with all the available currencies*</res>
        <cmd>currency</cmd>
        <res>Sends info about currency</res>
        <cmd>a b [amount]</cmd>
        <res>Converts amount of a to b</res>        
        </example>
        """
        now = pendulum.now().timestamp()
        needs_update = lambda x: True if x is None else now - x > self.update_time
        # No arguments were passed, and should display all available currencies
        if curFrom is None:
            if needs_update(self.currencies[1]):
                async with aiohttp.ClientSession() as session:
                    usage = await self.get_usage(session)
                    if usage < 90: await self.update_currencies(session)
            # Get a list of all currencies and sort it
            keys = list(self.currencies[0].keys())
            keys.sort()
            formatted = []
            for key in keys:
                c = self.currencies[0][key]
                # Format so its like "USD - United States Dollar"
                formatted.append(f"{key} - {c['currencyName']}")
            
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
        # If curFrom is not None and curTo is, display info about given currency
        # {currencyName} - {currencySymbol}
        elif curTo is None:
            if needs_update(self.currencies[1]):
                async with aiohttp.ClientSession() as session:
                    usage = await self.get_usage(session)
                    if usage < 90: await self.update_currencies(session)
            curFrom = curFrom.upper()
            info = self.currencies[0].get(curFrom)
            if info is None:
                await ctx.send(f'Unknown currency! do `{self.bot.command_prefix}money` to see a list of all available ones.')
            else:
                name = info['currencyName']
                symbol = info.get('currencySymbol')
                await ctx.send(f"{name}{' - '+symbol if symbol else ''}")
        # Converts curFrom to curTo, as they both aren't None
        else:
            curFrom = curFrom.upper()
            curTo = curTo.upper()
            if curFrom == curTo:
                return await ctx.send('no')

            if needs_update(self.currencies[1]):
                async with aiohttp.ClientSession() as session:
                    usage = await self.get_usage(session)
                    if usage < 90: await self.update_currencies(session)

            # Check if they are valid currencies
            if curFrom not in self.currencies[0] or curTo not in self.currencies[0]:
                return await ctx.send(f'Unknown currency! do `{self.bot.command_prefix}money` to see a list of all available ones.')
           
            amount = amount or 1
            try:
                amount = float(amount)
            except ValueError:
                return await ctx.send('Invalid amount')

            if amount == 0 or not math.isfinite(amount):
                return await ctx.send('no')

            async with aiohttp.ClientSession() as session:
                # Updating curFrom
                tmp = self.currency_rates.get(curFrom)
                if needs_update(tmp[1] if tmp is not None else None):
                    usage = await self.get_usage(session)
                    if usage < 90: await self.update_currency(session, curFrom)
                # Updating curTo
                tmp = self.currency_rates.get(curTo)
                if needs_update(tmp[1] if tmp is not None else None):
                    usage = await self.get_usage(session)
                    if usage < 90: await self.update_currency(session, curTo)
                    
                val = self.convert_currency(curFrom, curTo, amt=amount)
                await ctx.send(f'{amount} {curFrom} is about {val:.2f} {curTo}')

def setup(bot):
    bot.add_cog(Money(bot))