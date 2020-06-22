import discord

class Option:
    __slots__ = ('default', 'type', 'description')
    def __init__(self, default, _type, description: str):
        self.default = default
        self.type = _type
        self.description = description

class GuildFeatures:
    __slots__ = ('db', 'default_config')
    def __init__(self, db):
        self.db = db.guild_features
        self.default_config = {
            'quote_links': Option(False, bool, 'Automatically quotes message links sent in chat'),
            'gd_updates': Option(None, discord.TextChannel, 'Channel in which to send GD level updates such as new rated levels, weekly and daily')
        }

    def defaults(self):
        return dict((key, value.default) for key, value in self.default_config.items())

    async def init_guild(self, guild_id: int):
        return await self.db.insert_one({
            'id': guild_id,
            **self.defaults()
        })

    async def remove_guild(self, guild_id: int):
        await self.db.delete_one({'id': guild_id})

    async def get_guild(self, guild_id: int):
        return await self.db.find_one({'id': guild_id})

    async def get_option(self, guild_id: int, option: str):
        return (await self.db.find_one({'id': guild_id}, {option: True})).get(option, self.default_config[option].default)

    async def update_guild(self, guild_id: int, update: dict):
        return await self.db.update_one({'id': guild_id}, update)

    async def set_option(self, guild_id: int, option: str, value):
        return await self.update_guild(guild_id, {'$set': {option: value}})