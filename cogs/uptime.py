import discord
import asyncio

async def uptime(bot):
    await bot.wait_until_ready()
    bot.uptime = 0 
    while not bot.is_closed():
        await asyncio.sleep(10)
        bot.uptime += 10

def setup(bot):
    bot.loop.create_task(uptime(bot))
    
