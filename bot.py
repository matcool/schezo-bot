import discord
from discord.ext import commands
import json
import glob
import time
import os
import motor.motor_asyncio as motor

class Schezo(commands.Bot):
    def __init__(self):
        if not os.path.exists('bot_config.json'):
            raise FileNotFoundError('Could not find "bot_config.json". Make sure to copy and rename the template and then change the values.')
        with open('bot_config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        super().__init__(command_prefix=self.config['prefix'])
        self.start_time = time.time()
        self._cogs_loaded = False
        self.db_client = motor.AsyncIOMotorClient('localhost', 27017)
        self.db = self.db_client[self.config['dbname']]

    @property
    def uptime(self):
        return time.time() - self.start_time

    async def on_ready(self):
        print(f'Logged in as {self.user}')
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
    try:
        await ctx.message.add_reaction('🆗')
    except discord.DiscordException:
        pass

bot.run()