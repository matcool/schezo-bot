from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
import asyncio
import aiohttp
import json
import datetime
import re
#import upsidedown

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

    def get_rank(self, player):

        rank = None
        rank = player.get("packageRank") or rank
        rank = player.get("newPackageRank") or rank
        rank = player.get("monthlyPackageRank") or rank
        rank = player.get("rank") or rank
        rank_ = player.get("prefix")
        if rank_: rank = re.findall(r"§\w\[(.+)\]",rank_)[0]
        
        color = "9e9e9e"
        if rank:
            rank = rank.replace("_PLUS","+")
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

        return (rank,color)
        

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def bwstats(self,ctx,name):
        js = await self.get_player(name)
        if not js:
            await ctx.send("Player not found.")
            return
        
        bw = js["player"].get("stats").get("Bedwars")
        ach = js["player"].get("achievements",{})

        name = js["player"]["displayname"]

        if bw == None:
            await ctx.send("No bedwars stats found for that player.")
            return

        prefix = self.get_rank(js["player"])[0] or ''
        if prefix: prefix = f"[{prefix}] "
        
        bwstar = str(ach.get("bedwars_level"))
        wins = str(ach.get("bedwars_wins"))
        winstreak = str(bw.get("winstreak"))
        kills = str(bw.get("kills_bedwars", 0))
        fkills = str(bw.get("final_kills_bedwars", 0))
        tkills = str(int(kills) + int(fkills))
        lootchests = int(bw.get("bedwars_boxes"))

        
        coins = str(bw.get("coins",0))
        for i in range(3,len(coins),3): coins = coins[:-i]+","+coins[-i:]

        
        embed = discord.Embed(title=prefix+name+"'s Hypixel Bedwars stats", colour=int("ff7575", 16))
        embed.set_thumbnail(url="https://minotar.net/helm/{}/256.png".format(name))
        
        embed.add_field(name="Bedwars Level", value=bwstar+"\N{WHITE MEDIUM STAR}", inline=False)
        embed.add_field(name="Wins", value=wins+" Total wins\nCurrent winstreak : "+winstreak, inline=True)
        embed.add_field(name=tkills+" Total kills", value=kills+" Kills\n"+fkills+" Final kills", inline=True)
        embed.add_field(name="Items", value=f"{coins} Coins\n{lootchests} Loot Chest"+('s' if int(lootchests) > 1 else ""), inline=True)
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
        prefix = self.get_rank(js["player"])[0] or ''
        if prefix: prefix = f"[{prefix}] "

        solokills = sw.get("kills_solo","No")
        solowins = sw.get("wins_solo","No")
        teamkills = sw.get("kills_team","No")
        teamwins = sw.get("wins_team","No")
        coins = sw.get("coins","No")
        souls = sw.get("souls","No")
        tokens = sw.get("cosmetic_tokens","No")
        lootchests = sw.get("skywars_chests","No")
        #winstreak = sw.get("winstreak")

        coins = str(coins)
        for i in range(3,len(coins),3): coins = coins[:-i]+","+coins[-i:]
        
        embed = discord.Embed(title=f"{prefix+name}'s Hypixel Skywars Stats", colour=int("f4e842",16))
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

        rank, color = self.get_rank(player)
                
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
        #if name == "Dinnerbone":
        #    displayname = upsidedown.transform(displayname)
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
        embed.add_field(name="ach points", value=str(achpoints)+" (not acurate at all)", inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(70,60,BucketType.default)
    @commands.command()
    async def parkourstats(self,ctx,name,lobby="Bedwars"):
        #name = "alejandro_114"
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
