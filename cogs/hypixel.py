from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import asyncio
import aiohttp
import json
import datetime
import re
import upsidedown

class Hypixel:
    def __init__(self, bot):
        self.bot = bot
        self.achievements = None

    async def get_achievements(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://raw.githubusercontent.com/HypixelDev/PublicAPI/master/Documentation/misc/Achievements.json') as r:
                self.achievements = json.loads(await r.read())
                self.achievements = self.achievements["achievements"]
        
    apikey = "3dac2378-53fb-4d5e-992d-e260f2512960"
    async def get_player(self,player):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.hypixel.net/player?key='+self.apikey+'&name='+player) as r:
                js = await r.json()
        if not js["success"] or not js["player"]:
            return None
        return js
        
    async def get_friends(self,uuid):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.hypixel.net/friends?key='+self.apikey+'&uuid='+uuid) as r:
                js = await r.json()
        if not js["success"] or not js["records"]:
            return None
        return js

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def bwstats(self,ctx,name):
        js = await self.get_player(name)
        if not js:
            await ctx.send("Player not found.")
            return
        
        try:
            lo = js["player"]["stats"]["Bedwars"]
            del lo
        except KeyError:
            await ctx.send("No bedwars stats found for that player.")
            return
        embed = discord.Embed(title=name+"'s Hypixel Bedwars stats", colour=int("ff7575", 16))
        embed.set_thumbnail(url="https://minotar.net/helm/{}/256.png".format(name))

        ach = js["player"]["achievements"]
        bw = js["player"]["stats"]["Bedwars"]

        
        bwstar = str(ach["bedwars_level"])
        embed.add_field(name="Bedwars Level", value=bwstar+"\N{WHITE MEDIUM STAR}", inline=False)

        wins = str(ach["bedwars_wins"])
        winstreak = str(bw["winstreak"])
        embed.add_field(name="Wins", value=wins+" Total wins\nCurrent winstreak : "+winstreak, inline=True)

        try: kills = str(bw["kills_bedwars"])
        except KeyError: kills = "0"
        try: fkills = str(bw["final_kills_bedwars"])
        except KeyError: fkills = "0"
        tkills = str(int(kills) + int(fkills))
        embed.add_field(name=tkills+" Total kills", value=kills+" Kills\n"+fkills+" Final kills", inline=True)

        
        coins = str(bw["coins"])
        for i in range(3,len(coins),3):
            coins = coins[:-i]+","+coins[-i:]
        lootchests = str(bw["bedwars_boxes"])
        embed.add_field(name="Items", value=f"{coins} Coins\n{lootchests} Loot Chest"+(s if int(lootchests) > 1 else ""), inline=True)
        await ctx.send(embed=embed)

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def swstats(self,ctx,name):
        js = await self.get_player(name)
        if not js:
            await ctx.send("Player not found.")
            return
        
        sw = js["player"].get("stats").get("SkyWars")
        if not sw:
            await ctx.send("No bedwars stats found for that player.")
            return
        
        name = js["player"]["displayname"]
        solokills = sw.get("kills_solo")
        solowins = sw.get("wins_solo")
        teamkills = sw.get("kills_team")
        teamwins = sw.get("wins_team")
        coins = sw.get("coins")
        souls = sw.get("souls")
        tokens = sw.get("cosmetic_tokens")
        lootchests = sw.get("skywars_chests")
        #winstreak = sw.get("winstreak")
        tokens = "No" if not tokens else tokens
        lootchests = "No" if not lootchests else lootchests

        coins = str(coins)
        for i in range(3,len(coins),3): coins = coins[:-i]+","+coins[-i:]
        
        embed = discord.Embed(title=f"{name}'s Hypixel Skywars Stats", colour=int("f4e842",16))
        embed.set_thumbnail(url="https://minotar.net/helm/{}/256.png".format(name))
        
        embed.add_field(name="Solo",value=f"{solokills} Kills\n{solowins} Wins",inline=True)
        embed.add_field(name="Team",value=f"{teamkills} Kills\n{solowins} Wins",inline=True)
        embed.add_field(name="Items",value=f"{coins} Coins\n{souls} Souls",inline=True)
        embed.add_field(name="Items",value=f"{tokens} Tokens\n{lootchests} Loot Chests",inline=True)
        await ctx.send(embed=embed)
        

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def hypixel(self,ctx,name):
        if self.achievements == None:
            await self.get_achievements()

        player = await self.get_player(name)
        if not player:
            await ctx.send("Player not found.")
            return
        player = player["player"]
        name = player["displayname"]
        uuid = player["uuid"]

        #getting rank
        rank = None
        rank_ = player.get("packageRank")
        if rank_: rank = rank_
        rank_ = player.get("newPackageRank")
        if rank_: rank = rank_
        rank_ = player.get("monthlyPackageRank")
        if rank_: rank = rank_
        rank_ = player.get("rank")
        if rank_: rank = rank_
        rank_ = player.get("prefix")
        if rank_:
            rank = re.findall(r"§\w\[(.+)\]",rank_)[0]
        
        if rank: rank = rank.replace("_PLUS","+")
        color = "9e9e9e"
        if rank:
            if rank.startswith("VIP"):
                color = "3cff2b"
            elif rank.startswith("MVP"):
                color = "0cfaff"
            if rank == "SUPERSTAR":
                rank = "MVP++"
                color = "FFAA00"
            if rank in ("ADMIN","YOUTUBER","MOJANG","SLOTH","OWNER"):
                color = "FF5555"
            if rank == "HELPER":
                color = "4949DA"
            if rank == "MOD":
                color = "59B330"
                
        #achievements points
        achpoints = 0
        achievs = player.get("achievementsOneTime")
        for a in achievs:
            try:
                cat = a.split("_")[0]
                aname = a[a.find("_")+1:].upper()
                ach = self.achievements[cat]["one_time"][aname]
                achpoints += ach["points"]
            except KeyError:
                pass

        
        displayname = f"[{rank}] {name}" if rank else name
        if name == "Dinnerbone":
            displayname = upsidedown.transform(displayname)
        embed = discord.Embed(title=displayname, colour=int(color, 16))
        embed.set_thumbnail(url="https://minotar.net/helm/{}/256.png".format(name))

        karma = player.get("karma")
        nfriends = 0
        friends = await self.get_friends(uuid)
        if friends:
            nfriends = len(friends["records"])
        if not nfriends: nfriends = "himself"

        embed.add_field(name="karma", value=karma, inline=False)
        embed.add_field(name="friends", value=nfriends, inline=False)
        embed.add_field(name="ach points", value=str(achpoints)+" (not acurate at all", inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def parkourstats(self,ctx,name,lobby="Bedwars"):
        js = await self.get_player(name)
        if not js:
            await ctx.send("Player not found.")
            return
        js = js["player"]["parkourCompletions"]
        js = js.get(lobby)
        if not js:
            await ctx.send("not found or smth")
            return
        lowest = None
        attempts = len(js)
        for d in js:
            if not lowest:
                lowest = d["timeTook"]
                continue
            
            if d["timeTook"] < lowest:
                lowest = d["timeTook"]
                continue
        m,s = divmod(int(str(lowest)[:-3]),60)
        ms = str(lowest)[-3:]
        m,s = (str(m),str(s))
        d0 = lambda x: "00"[len(x):]+x
        t0 = lambda x: "000"[len(x):]+x
        formattedtime = "{}:{}:{}".format(d0(m),d0(s),t0(ms))
        del d0,t0,m,s,ms
        embed = discord.Embed(title=f"{name}'s parkour stats on the {lobby} parkour", colour=int("ff7738", 16))
        embed.set_thumbnail(url="https://minotar.net/helm/{}/256.png".format(name))
        embed.add_field(name="Best time", value=formattedtime, inline=False)
        embed.add_field(name="Finished attempts", value=attempts, inline=False)
        await ctx.send(embed=embed)
        
        
        

def setup(bot):
    bot.add_cog(Hypixel(bot))
