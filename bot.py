import discord
from discord.ext import commands
import json
import asyncio
import glob

class Schezo(commands.Bot):
    def __init__(self):
        with open('bot_config.json') as file:
            self.config = json.load(file)
        super().__init__(command_prefix=self.config['prefix'])
        self.loop.create_task(self.uptime())
        self._cogs_loaded = False

    async def uptime(self):
        self.uptime = 0 
        while not bot.is_closed():
            await asyncio.sleep(10)
            self.uptime += 10

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        game = discord.Activity(name=self.config['game'], type=discord.ActivityType.watching)
        await self.change_presence(activity=game)
        self.load_cogs()

    def get_cogs(self):
        files = glob.glob('cogs/*.py')
        # Replace / or \ with . and remove .py at the end
        return map(lambda p: p.replace('\\','.').replace('/','.')[:-3], files)

    def load_cogs(self):
        if self._cogs_loaded: return
        self._cogs_loaded = True
        for cog in self.get_cogs():
            self.load_extension(cog)

    def unload_cogs(self):
        self._cogs_loaded = False
        extensions = tuple(self.extensions.keys())
        for cog in extensions:
            self.unload_extension(cog)

    def run(self):
        super().run(self.config['token'])

bot = Schezo()

@bot.command(hidden=True, aliases=['rc'])
@commands.is_owner()
async def reloadcogs(ctx):
    ctx.bot.unload_cogs()
    ctx.bot.load_cogs()
    await ctx.send('done')

bot.run()