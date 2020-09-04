import discord
from discord.ext import commands

class VC(commands.Cog):
    __slots__ = 'bot', 'overwrite_name'
    def __init__(self, bot):
        self.bot = bot
        self.overwrite_name = 'General'

    @commands.command(hidden=True)
    @commands.guild_only()
    async def boom(self, ctx: commands.Context):
        for vc in ctx.guild.voice_channels:
            if ctx.author in vc.members:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(vc)
                else:
                    await vc.connect()

                if ctx.voice_client and not ctx.voice_client.is_playing():
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('./assets/boom.mp3'), volume=0.6)
                    ctx.voice_client.play(source)

                return
        else:
            await ctx.send('u not in vc')

    @commands.command(hidden=True)
    @commands.guild_only()
    async def shawty(self, ctx: commands.Context):
        for vc in ctx.guild.voice_channels:
            if ctx.author in vc.members:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(vc)
                else:
                    await vc.connect()

                if ctx.voice_client and not ctx.voice_client.is_playing():
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('./assets/shawty.mp3'), volume=0.6)
                    ctx.voice_client.play(source)

                return
        else:
            await ctx.send('u not in vc')

def setup(bot):
    bot.add_cog(VC(bot))