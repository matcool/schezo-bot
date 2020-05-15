from discord.ext import commands
import discord
import asyncio

class Paginator:
    __slots__ = ('_get_embed', '_is_coroutine', 'clear_reactions', 'delete_message', 'n_pages', 'message', 'timeout')

    def __init__(self, n_pages: int, get_embed, clear_reactions: bool=True, delete_message: bool=True, timeout: float=10.0):
        self._get_embed = get_embed
        self._is_coroutine = asyncio.iscoroutine(self._get_embed)
        self.n_pages = n_pages
        self.message: discord.Message = None
        self.timeout = timeout
        self.clear_reactions = clear_reactions
        self.delete_message = delete_message

    async def get_embed(self, i: int) -> discord.Embed:
        if self._is_coroutine: return await self._get_embed(i)
        return self._get_embed(i) 

    async def start(self, ctx: commands.Context):
        index = 0
        self.message = await ctx.send(embed=await self.get_embed(index))

        await self.message.add_reaction('◀️')
        await self.message.add_reaction('⏹️')
        await self.message.add_reaction('▶')

        def check(payload):
            return payload.message_id == self.message.id and payload.user_id == ctx.author.id and str(payload.emoji) in '◀️⏹️▶'

        while True:
            done, pending = await asyncio.wait([
                ctx.bot.wait_for('raw_reaction_add', check=check),
                ctx.bot.wait_for('raw_reaction_remove', check=check)
            ], return_when=asyncio.FIRST_COMPLETED, timeout=self.timeout)
            
            for future in pending:
                future.cancel()

            if not done:
                return await self.stop(idle=True)

            try:
                payload = done.pop().result()
            except Exception:
                return await self.stop(idle=True)
            else:
                edit = True
                if str(payload.emoji) == '▶':
                    edit = index != self.n_pages - 1
                    index = min(index + 1, self.n_pages - 1)
                elif str(payload.emoji) == '◀️':
                    edit = index != 0
                    index = max(index - 1, 0)
                else:
                    await self.stop()
                    return
                if edit: await self.message.edit(embed=await self.get_embed(index))

    async def stop(self, idle: bool=False):
        if self.clear_reactions:
            try:
                await self.message.clear_reactions()
            except discord.Forbidden:
                pass
        if self.delete_message and not idle:
            await self.message.delete()
