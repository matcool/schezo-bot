from discord.ext import commands
import discord
import asyncio
from PIL import Image, ImageDraw, ImageColor, ImageFont
import random
import io
from functools import partial
import aiohttp

class ImageStuff:
    def __init__(self,bot):
        self.bot = bot


    async def get_page(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.read()

        return result


    async def get_avatar(self, user) -> bytes:
        avatar_url = user.avatar_url_as(format="png")

        async with aiohttp.ClientSession() as session:
            async with self.session.get(avatar_url) as response:
                avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def tenprintpil() -> io.BytesIO:
        l = Image.new('RGB', (500,500), (255,255,255))
        n = 10
        div = l.width/n
        d = ImageDraw.Draw(l)
        for y in range(n):
            for x in range(n):
                r = random.randint(0,1)
                if r == 0:
                    d.line((div*x,y*div,div*x+div,y*div+div),fill="#000000",width=2)
                else:
                    d.line((div*x+div,y*div,div*x,y*div+div),fill="#000000",width=2)
        imgobject = io.BytesIO()
        l.save(imgobject,format='PNG')
        imgobject.seek(0)
        return imgobject
    
    @commands.command()
    async def tenprint(self,ctx):
        """maze like structure (not a maze)"""
        async with ctx.typing():
            p = partial(self.tenprintpil)
            img = await self.bot.loop.run_in_executor(None, p)
            await ctx.send(file=discord.File(img, 'tenprint.png'))

    @staticmethod
    def nicehackspil(avatar,name,color,msg) -> io.BytesIO:
        l = Image.new('RGB', (219,64), (54,57,62))
        
        im = Image.open(io.BytesIO(avatar))
        im = im.convert("RGBA")
        im = im.resize((36,36), Image.ANTIALIAS)
        avav = Image.new("RGBA",im.size,"#36393e")
        avav.paste(im,(0,0),mask=im.getchannel("A"))
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size,Image.ANTIALIAS)
        avav.putalpha(mask)
        bg = Image.new("RGBA",im.size,"#36393e")
        bg.paste(avav,(0,0),mask=avav.getchannel("A"))
        del avav
        del mask
        del draw
        del im

        
        d = ImageDraw.Draw(l)
        txtf = ImageFont.truetype("stuff/Whitney-Book.otf", 15)
        namef = ImageFont.truetype("stuff/Whitney-Book.otf", 16)
        timef = ImageFont.truetype("stuff/Whitney-Book.otf", 10)

        widttht = d.textsize(msg,txtf)[0]+68+5
        space = d.textsize(name,namef)[0]+68+4
        today = d.textsize("Today at 6:30 PM",timef)[0]+space+8
        if today > widttht:
            l = l.resize((today,64))
        else:
            l = l.resize((widttht,64))
        d = ImageDraw.Draw(l)
        d.text((68,34), msg, font=txtf, fill="#ffffff")
        d.text((68,10), name, font=namef, fill=color)
        d.text((space,16), "Today at 6:30 PM", font=timef, fill="#50555B")
        
        l.paste(bg, (14,13))
        
        tmp = io.BytesIO()
        l.save(tmp,format='PNG')
        tmp.seek(0)
        return tmp

    @commands.command()
    async def nicehacks(self,ctx,*,msg):
        async with ctx.typing():
            if msg.find(" ") != -1:
                uid = msg.split(" ")[0]
            else:
                uid = None
                
            try:
                uid = int(uid)
                msg = msg[msg.find(" ")+1:]
            except (ValueError,TypeError):
                uid = None
                pass

            if uid:
                if ctx.guild: m = ctx.guild.get_member(uid)
                else: m = bot.get_user(uid)
            else:
                m = ctx.author

            if not m:
                await ctx.send("Invalid id.")
                return
            
            av = await self.get_avatar(m)

            if isinstance(m, discord.Member):
                c = m.colour.to_rgb()
                if m.colour == discord.Colour.default():
                    c = (255,255,255)
            else:
                c = (255,255,255)
            

            p = partial(self.nicehackspil,av,m.display_name,c,msg)
            img = await self.bot.loop.run_in_executor(None, p)
            await ctx.send(file=discord.File(img, 'notme.png'))

    @staticmethod
    def cvoltonpil(image) -> io.BytesIO:
        cvolton = Image.open("stuff/cvolton.png")
        cvolton = cvolton.convert("RGBA")
        bg = Image.open(image)
        bg = bg.convert("RGBA")
        bg = bg.resize(cvolton.size, Image.ANTIALIAS)
        bg.paste(cvolton,(0,0),mask=cvolton.getchannel("A"))
        
        tmp = io.BytesIO()
        bg.save(tmp,format='PNG')
        tmp.seek(0)
        return tmp

    @commands.command()
    async def cvolton(self,ctx):
        try:
            att = ctx.message.attachments
            img = att[0]
        except Exception:
            await ctx.send("No attachments found.")
            return
        
        supportedformats = (".png",".jpg",".jpeg",".gif")
        download = False
        for i in supportedformats:
            if img.filename.endswith(i):
                download = True
                break
        if not download:
            return

        print(img)
        image = io.BytesIO()
        await img.save(image)
        p = partial(self.cvoltonpil,image)
        img = await self.bot.loop.run_in_executor(None, p)
        await ctx.send(file=discord.File(img, 'cvolton.png'))
    
    @staticmethod
    def achievementpil(text) -> io.BytesIO:    
        white = (255,255,255)
        imgm = Image.open('stuff/achievment.png').convert('RGBA')
        txtsize = 16
        fnt = ImageFont.truetype('stuff/Minecraftia.ttf', txtsize)
        d = ImageDraw.Draw(imgm)
        d.fontmode = "1"
        d.text((60,28), text, font=fnt, fill=white)
        
        imgobject = io.BytesIO()
        imgm.save(imgobject,format='PNG')
        imgobject.seek(0)
        return imgobject
        
    @commands.command()
    async def achievement(self,ctx,*,text):
        p = partial(self.achievementpil,text)
        img = await self.bot.loop.run_in_executor(None, p)
        await ctx.send(file=discord.File(img, 'maincra.png'))

    @staticmethod
    def inspquotepil(image) -> io.BytesIO:    
        over = Image.open("stuff/dhl.png")
        over = over.convert("RGBA")
        bg = Image.open(io.BytesIO(image))
        bg = bg.convert("RGBA")
        bg = bg.resize(over.size, Image.ANTIALIAS)
        bg.paste(over,(0,0),mask=over.getchannel("A"))
        
        bg = bg.convert("RGB")
        tmp = io.BytesIO()
        bg.save(tmp,format='JPEG', quality=20)
        tmp.seek(0)
        return tmp
        
    @commands.command(aliases=['inspirationalquote','inspirational'])
    async def inspquote(self,ctx):
        """Sends a inspirational quote."""
        tmp = await self.get_page("https://source.unsplash.com/random")
        p = partial(self.inspquotepil,tmp)
        img = await self.bot.loop.run_in_executor(None, p)
        await ctx.send(file=discord.File(img, 'quote.jpg'))
        
    @commands.command()
    async def inspirobot(self,ctx):
        url = await self.get_page("https://inspirobot.me/api?generate=true")
        url = str(url,encoding='utf-8')
        await ctx.send(url)

        

    
            
def setup(bot):
    bot.add_cog(ImageStuff(bot))
