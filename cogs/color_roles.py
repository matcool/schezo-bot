import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from pymongo import ReturnDocument

class ColorRoles(commands.Cog):
    __slots__ = 'bot', 'db', 'overwrite_name'
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.color_roles
        self.overwrite_name = 'Utility'

    async def init_guild(self, guild_id: int):
        return await self.db.insert_one({
            'guild_id': guild_id,
            # using 0 and 1 instead of booleans so i can do a xor, since there is no way of toggling booleans in one operation
            'disabled': 0,
            'roles': {}, # user_id: role_id
            'restrict': None # restrict system to users with this role
        })

    async def has_guild(self, guild_id: int) -> bool:
        return await self.db.count_documents({'guild_id': guild_id}) != 0

    async def get_guild(self, guild_id: int):
        return await self.db.find_one({'guild_id': guild_id})

    async def toggle_guild(self, guild_id: int) -> bool:
        return (await self.db.find_one_and_update(
            {'guild_id': guild_id},
            {'$bit': {'disabled': {'xor': 1}}},
            return_document=ReturnDocument.AFTER
        )).get('disabled')
    
    async def delete_guild(self, guild_id: int):
        await self.db.delete_one({'guild_id': guild_id})

    async def get_user_role(self, guild_id: int, user_id: int) -> int:
        guild = await self.get_guild(guild_id)
        return guild['roles'].get(str(user_id)) # mongodb can only have keys as string

    async def set_user_role(self, guild_id: int, user_id: int, role_id: int):
        await self.db.update_one({'guild_id': guild_id}, {'$set': {f'roles.{user_id}': role_id}})

    async def set_restrict(self, guild_id: int, role_id: int):
        await self.db.update_one({'guild_id': guild_id}, {'$set': {'restrict': role_id}})

    @commands.group(invoke_without_command=True, aliases=['color_roles', 'cr'])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, BucketType.member)
    async def colorroles(self, ctx: commands.Context, color=None):
        """
        Sets up color roles system for this server.
        This is **NOT recommended for big servers**, as this can make a role for every member that runs the command.
        This requires the bot to have the manage roles permission, and every role will be added to the very bottom, \
        which means it will require you to have no color on all other roles like member and such.
        Examples::
        > init
        Starts the color roles system for this server. Requires you to have the manage roles permission
        > ff0000
        Creates (or edits if already exists) a role for you with the given color
        > #ff0000
        Same as above
        > toggle
        Toggles the color system. Disabling it makes it so new roles can't be made and existing ones can't be changed
        > delete
        Deletes color system data, **along with all the color roles**
        > restrict Special
        Restricts color system to given role (can be name or id)
        > restrict
        Resets restrict role
        """
        info = await self.get_guild(ctx.guild.id)
        if info is None:
            if color is None:
                return await ctx.send(f'Server does not have the system enabled')
            else:
                return await ctx.send(f'Do `{ctx.prefix}help color_roles` for more info')
        if color is None:
            role_id = await self.get_user_role(ctx.guild.id, ctx.author.id)
            role = ctx.guild.get_role(role_id) if role_id else None
            if role is None:
                await ctx.send(f'Do `{ctx.prefix}help color_roles` for more info')
            else:
                color = f'{role.color.value:x}'
                await ctx.send(f'You currently have the color: **#{color}**', embed=discord.Embed().set_image(url=f'https://dummyimage.com/100x100/{color}/fff&text=+'))
            return
        elif info['disabled']:
            return await ctx.send(f'Color system is currently disabled on this server.')
        elif info.get('restrict'):
            role = ctx.guild.get_role(info['restrict'])
            if role is None or role not in ctx.author.roles:
                return await ctx.send(f'Color system is only allowed to those who have the "{role}" role.')
        if color[0] == '#': color = color[1:]
        if len(color) != 6:
            return await ctx.send('Color must be 6 hex digits')
        try:
            color = int(color, 16)
        except ValueError:
            return await ctx.send('Color must be 6 hex digits')

        role_id = await self.get_user_role(ctx.guild.id, ctx.author.id)
        role = ctx.guild.get_role(role_id) if role_id else None
        # make new role
        if role_id is None or role is None:
            role = await ctx.guild.create_role(name=f'color {ctx.author.name}', color=discord.Color(color), reason='Color system role')
            await role.edit(position=1)
            await ctx.author.add_roles(role)
            await self.set_user_role(ctx.guild.id, ctx.author.id, role.id)
        # edit existing role
        else:
            await role.edit(color=discord.Color(color))
        await ctx.send('done')

    @colorroles.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def init(self, ctx):
        await self.init_guild(ctx.guild.id)
        await ctx.send('done')

    @colorroles.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def toggle(self, ctx):
        if await self.has_guild(ctx.guild.id):
            state = await self.toggle_guild(ctx.guild.id)
            state = 'disabled' if state else 'enabled'
            await ctx.send(f'System is now {state}')
        else:
            await ctx.send(f'System must be initialized first, use `{ctx.prefix}colorroles init`')
    
    @colorroles.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def delete(self, ctx):
        if await self.has_guild(ctx.guild.id):
            await ctx.send('Are you sure you want to disable the system and **delete** all color roles? (reply with `y` to confirm)')
            msg = await self.bot.wait_for('message', check=lambda msg: msg.author.id == ctx.author.id, timeout=10)
            if msg.content.lower() != 'y':
                return await ctx.send('Cancelling')
            data = await self.get_guild(ctx.guild.id)
            await self.delete_guild(ctx.guild.id)
            for role_id in data['roles'].values():
                role = ctx.guild.get_role(role_id)
                await role.delete()
        else:
            await ctx.send('its not even on')

    @colorroles.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def restrict(self, ctx, role: discord.Role=None):
        if not await self.has_guild(ctx.guild.id):
            return await ctx.send('its not even on')
        
        if role is None:
            await self.set_restrict(ctx.guild.id, None)
            await ctx.send('Restrict role has been reset')
        else:
            await self.set_restrict(ctx.guild.id, role.id)
            await ctx.send(f'Restrict role has been set to {role.name}')

async def setup(bot):
    await bot.add_cog(ColorRoles(bot))