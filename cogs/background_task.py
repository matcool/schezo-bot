import discord
import asyncio
import time
from discord.ext import commands    

bdaymsg1 = ":tada: :tada: <@168770585306857472> happy bday!!! :blush:\nim sleep now probably so matbot will do my job!! ok have nice day! :grin:\n (i hope this got sent at the right time)"
bdaymsg2 = "i will now do the tada dance!!"
coneid = 464580016613752842

async def my_bg_task(bot):
    await bot.wait_until_ready()   
    channel = bot.get_channel(418209286905135107) # normal channel
    #channel = bot.get_channel(295953725271572481) # my channel debug
    while not bot.is_closed():
        t = time.localtime()
        if t.tm_mday == 6 and t.tm_hour >= 1:
            await channel.send(bdaymsg1)
            await asyncio.sleep(5)
            await channel.send(bdaymsg2)
            await asyncio.sleep(2)
            counter = 0
            cone = bot.get_emoji(coneid)
            emojis = [":tada:",cone]
            msg = await channel.send(cone)
            while counter < 10:
                await asyncio.sleep(1)
                await msg.edit(content=emojis[counter%2])
                counter += 1
            await asyncio.sleep(1)
            await msg.edit(content=":heart:")
            return
        await asyncio.sleep(60)

def setup(bot):
    bot.loop.create_task(my_bg_task(bot))
    
