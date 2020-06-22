import discord
from discord.ext import commands
import json
import glob
import time
import os
import motor.motor_asyncio as motor
import logging
import sys
from cogs.utils.guild_features import GuildFeatures

class Schezo(commands.Bot):
    __slots__ = 'config', 'start_time', '_cogs_loaded', 'db_client', 'db', 'logger', 'gf'
    def __init__(self):
        if not os.path.exists('bot_config.json'):
            raise FileNotFoundError('Could not find "bot_config.json". Make sure to copy and rename the template and then change the values.')
        with open('bot_config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        super().__init__(command_prefix=self.config['prefix'])
        self.start_time = time.time()
        self._cogs_loaded = False
        self.db_client = motor.AsyncIOMotorClient('localhost', 27017, retryWrites=self.config.get('retrywrites', True))
        self.db = self.db_client[self.config['dbname']]

        self.gf: GuildFeatures = GuildFeatures(self.db)

        self.logger = logging.getLogger('schezo')
        formatter = logging.Formatter('[{asctime} {levelname}] {message}', datefmt='%d/%m/%Y %H:%M', style='{')
        file_handler = logging.FileHandler('schezo.log', mode='w')
        file_handler.setFormatter(formatter)

        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

    @property
    def uptime(self):
        return time.time() - self.start_time

    async def on_ready(self):
        msg = f'Logged in as {self.user}'
        print(msg)
        self.logger.info(msg)
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
    modules = tuple(sys.modules.keys())
    for name in modules:
        if name.startswith('cogs.utils'):
            del sys.modules[name]
    ctx.bot.load_cogs()
    try:
        await ctx.message.add_reaction('🆗')
    except discord.DiscordException:
        pass

bot.run()