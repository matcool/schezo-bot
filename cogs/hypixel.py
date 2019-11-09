from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import asyncio
import aiohttp
import json
import datetime
from typing import Dict

class Hypixel(commands.Cog):
    __slots__ = 'bot', 'api_key'
    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.bot.config.get('hypixelkey')

    async def get_uuid(self, username: str) -> str:
        """
        ps: the mojang api only allows up to 600 requests per 10 minutes
        i'm not doing any checks for that since my bot isn't that popular
        """
        username = username.strip()
        if not username: raise Exception('Invalid username')
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{username}') as r:
                if r.status != 200: return
                data = await r.json()
        return data['id']
    
    async def get_player(self, uuid: str) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.hypixel.net/player', params={
                'key': self.api_key,
                'uuid': uuid
            }) as r:
                data = await r.json()
        if not data['success'] or not data['player']: return None
        return data['player']

    @commands.command()
    async def bwstats(self, ctx, username):
        uuid = await self.get_uuid(username)
        if not uuid: return await ctx.send('Player not found')
        
        player = await self.get_player(uuid)
        if not player: return await ctx.send('Player not found')
        
        bw = player.get('stats', {}).get('Bedwars')
        if not bw: return await ctx.send('No bedwars stats found for that player')

        ach = player.get('achievements', {})

        name = player['displayname']
        
        level = ach.get('bedwars_level', 0)
        wins = ach.get('bedwars_wins', 0)
        winstreak = bw.get('winstreak', 0)
        kills = bw.get('kills_bedwars', 0)
        final_kills = bw.get('final_kills_bedwars', 0)
        total_kills = kills + final_kills
        loot_chests = bw.get('bedwars_boxes', 0)

        coins = bw.get('coins', 0)
        coins = f'{coins:,}' # 10000 -> 10,000

        embed = discord.Embed(title=f"{name}'s Hypixel Bedwars stats", colour=0xff7575)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{name}/256.png')
        
        embed.add_field(name='Bedwars Level',
                        value=f'{level}\N{WHITE MEDIUM STAR}', inline=False)

        embed.add_field(name='Wins',
                        value=f'{wins} Total wins\nCurrent winstreak : {winstreak}', inline=True)

        embed.add_field(name=f'{total_kills} Total kills',
                        value=f'{kills} Kills\n{final_kills} Final kills', inline=True)

        embed.add_field(name='Items',
                        value=f"{coins} Coins\n{loot_chests} Loot Chest{'s' if loot_chests > 1 else ''}", inline=True)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Hypixel(bot))