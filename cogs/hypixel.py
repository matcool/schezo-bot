from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.misc import safe_div
from typing import Dict
import discord
import asyncio
import aiohttp
import json
import datetime

class Hypixel(commands.Cog):
    __slots__ = 'bot', 'api_key', 'overwrite_name'
    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.bot.config.get('hypixelkey')

        self.overwrite_name = 'Games'

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

    @commands.cooldown(70, 60, BucketType.default)
    @commands.command()
    async def bwstats(self, ctx, username):
        """Sends bedwars stats about given player"""
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

        kdr = safe_div(kills, bw.get('deaths_bedwars', 0))
        fkdr = safe_div(final_kills, bw.get('final_deaths_bedwars', 0))
        wlr = safe_div(wins, bw.get('losses_bedwars', 0))

        embed = discord.Embed(title=f"{name}'s Hypixel Bedwars stats", colour=0xff7575)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/256.png')
        
        embed.add_field(name='Bedwars Level',
                        value=f'{level}\N{WHITE MEDIUM STAR}', inline=False)

        embed.add_field(name='Wins',
                        value=f'{wins} Total wins\nWinstreak: {winstreak}', inline=True)

        embed.add_field(name=f'{total_kills} Total kills',
                        value=f'{kills} Kills\n{final_kills} Final kills', inline=True)

        embed.add_field(name='Items', inline=True,
                        value=f"{coins} Coins\n{loot_chests} Loot Chest{'s' if loot_chests > 1 else ''}")

        embed.add_field(name='Ratios', inline=True,
                        value=f'K/D: {kdr:.2f}\n'
                              f'Final K/D: {fkdr:.2f}\n'
                              f'W/L: {wlr:.2f}')

        await ctx.send(embed=embed)

    @commands.cooldown(70, 60, BucketType.default)
    @commands.command()
    async def swstats(self, ctx, username):
        """Sends skywars stats about given player"""
        uuid = await self.get_uuid(username)
        if not uuid: return await ctx.send('Player not found')
        
        player = await self.get_player(uuid)
        if not player: return await ctx.send('Player not found')
        
        sw = player.get('stats', {}).get('SkyWars')
        if not sw: return await ctx.send('No skywars stats found for that player')
        
        name = player['displayname']

        solo_kills = sw.get('kills_solo', 0)
        solo_wins = sw.get('wins_solo', 0)
        team_kills = sw.get('kills_team', 0)
        team_wins = sw.get('wins_team', 0)
        souls = sw.get('souls', 0)
        tokens = sw.get('cosmetic_tokens', 0)
        loot_chests = sw.get('skywars_chests', 0)

        coins = sw.get('coins', 0)
        coins = f'{coins:,}' # 10000 -> 10,000

        kdr = safe_div(sw.get('kills', 0), sw.get('deaths', 0))
        wlr = safe_div(sw.get('wins', 0), sw.get('losses', 0))
        
        embed = discord.Embed(title=f"{name}'s Hypixel Skywars stats", colour=0xf4e842)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/256.png')
        
        embed.add_field(name='Solo',
                        value=f'{solo_kills} Kills\n{solo_wins} Wins', inline=True)
        
        embed.add_field(name='Team',
                        value=f'{team_kills} Kills\n{solo_wins} Wins', inline=True)
        
        embed.add_field(name='Items',
                        value=f'{coins} Coins\n{souls} Souls', inline=True)
        
        embed.add_field(name='Items',
                        value=f'{tokens} Tokens\n{loot_chests} Loot Chests', inline=True)

        embed.add_field(name='Ratios', inline=True,
                        value=f'K/D: {kdr:.2f}\n'
                              f'W/L: {wlr:.2f}')

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Hypixel(bot))