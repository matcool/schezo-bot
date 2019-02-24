from discord.ext import commands
import discord
import asyncio
import random

class games(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	#variables
	snakeBool = False

	@commands.command(hidden=True,enabled=False)
	async def snake(self,ctx):
		if self.snakeBool:
			await ctx.send('Someone is playing this already')
			return
		self.snakeBool = True
		w = 10
		h = 15
		score = 0
		snake = [[0,4]]
		food = [6,6]
		KEY_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT = 0,1,2,3
		key = KEY_DOWN
		prevKey = key
		grid = eval('['+(('['+('0,'*h)[:-1]+'],')*w)[:-1]+']')
		msg = await ctx.send('hello')
		scor = await ctx.send('info')
		arrows = ('\N{Black Left-Pointing Triangle}','\N{Up-Pointing Small Red Triangle}','\N{Down-Pointing Small Red Triangle}','\N{Black Right-Pointing Triangle}','\N{Black Square for Stop}')
		for i in arrows: await msg.add_reaction(i)
		
		async def show():
			f = ''
			for y in range(h):
				c = ''
				for x in range(w):
					if grid[x][y] == 1: c += '\N{Nauseated Face}'
					elif grid[x][y] == 2: c += '\N{Red Apple}'
					elif grid[x][y] == 3: c += arrows[key]
					else: 
						c += '\N{Medium White Circle}' 
						#c += '\N{White Large Square}'
				c += '\n'
				f += c
			f += '\n'
			await msg.edit(content=f)
			
		def point(x,y,p):
			grid[x][y] = p
		point(food[0], food[1], 2)   
		frameC = 0
		inputFrameC = 0
		#idleframes = 0
		diemsg = 'GAME OVER'
		while True:
			reamsg = await ctx.get_message(msg.id)
			reas = reamsg.reactions
			for r in reas:
				if r.count > 1:
					users = await r.users().flatten()
					if ctx.author in users and r.emoji in arrows:
						await msg.remove_reaction(r.emoji,ctx.author)
						key = arrows.index(r.emoji)
						break
			if key == 4:
				diemsg = 'lol bye'
				break
			if frameC % 5 == 0:
				snake.insert(0, [snake[0][0] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1), snake[0][1] + (key == KEY_UP and -1) + (key == KEY_DOWN and 1)])
				if snake[0][0] == -1: snake[0][0] = w-1
				if snake[0][1] == -1: snake[0][1] = h-1
				if snake[0][0] == w: snake[0][0] = 0
				if snake[0][1] == h: snake[0][1] = 0
				if snake[0] in snake[1:]: break
				if snake[0] == food:
					food = []
					score += 1
					while food == []:
						food = [random.randint(1, w-2), random.randint(1, h-2)]
						if food in snake: food = []
					point(food[0], food[1], 2)
				else:	
					last = snake.pop()
					point(last[0], last[1], 0)
				point(snake[0][0], snake[0][1], 1)
				await show()
				infoo = 'last key : '+arrows[key]+'\n'
				infoo += 'score : '+str(score)
				infoo += '\ninputframeC '+str(inputFrameC)
				infoo += '\nprevkey :'+arrows[prevKey]
				await scor.edit(content=infoo)
				if key == prevKey: inputFrameC += 1
				else: inputFrameC = 0

			await asyncio.sleep(1/30)
			frameC += 1
			prevKey = key

			if inputFrameC > h + (w/2):
				diemsg = 'too much time idle'
				break
		await msg.edit(content=diemsg+'\n	Score:'+str(score))
		await scor.delete()
		await msg.clear_reactions()
		self.snakeBool = False




def setup(bot):
	bot.add_cog(games(bot))