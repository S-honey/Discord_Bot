import discord
from discord.ext import commands

game = discord.Game("뭔가 하는중")
bot = commands.Bot(command_prefix='ㄹㅇ ', status=discord.Status.online, activity=game)

@bot.event
async def on_ready():
    print('시스템 가동')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command(aliases=['안녕', 'hi', '안녕하세요', 'ㅎㅇ'])
async def hello(ctx):
    await ctx.send(f'{ctx.author.mention}님 안녕하세요!')

@bot.command()
async def 도움(ctx):
    embed = discord.Embed(title='도움말', description='제작 by않되어떡케', color = 0x00ff00)
    embed.add_field(name='1. 인사', value='ㄹㅇ 안녕', inline=False)
    embed.add_field(name='2. 운세 [~띠]', value='ㄹㅇ 오늘의[~띠] 운세', inline=False)
    await ctx.send(embed=embed)
    
@bot.command()
async def 운세(ctx, *, text):
    await ctx.send(text)

bot.run('Your Token')
