import discord
import os
import asyncio
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import openpyxl as xl
import pandas as pd
import random
import time
import re
import warnings
import urllib
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from urllib.parse import quote

# 오늘의 운세 크롤링 후 엑셀파일로 저장
def crawl_daily_fortune():
    url = 'https://unse.daily.co.kr/?p=zodiac'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    parent = soup.select_one('#card')
    children = parent.select('ul')      # select: 여러개의 요소 / select_one: 가장 첫번째 요소

    wb = xl.Workbook()
    children = parent.select('ul')      # select: 여러개의 요소 / select_one: 가장 첫번째 요소
    for i in children:
        lis = i.select('li')
        for n, li in enumerate(lis):
            if n == 0:
                animal = li.select_one('div > b').get_text()    # 태그 중 텍스트 추출
                total = li.select_one('div > p').get_text()
                ws = wb.create_sheet(animal+'띠')    # animal 이름으로 시트 생성
                ws.append([total])    
            else:
                year = li.select_one('span').get_text()
                luck = li.select_one('p').get_text()
                ws.append([year, luck])
    wb.save('fortune.xlsx')

def movie_rank():
    boxoffice = "https://movie.daum.net/ranking/boxoffice/weekly"
    #reservation_rank = "https://movie.daum.net/ranking/reservation"

    res1 = requests.get(boxoffice)
    res1.raise_for_status()

    bs1 = BeautifulSoup(res1.text, "lxml")

    parent = bs1.select_one('#mainContent')

    movie_ranks = parent.find_all("div", attrs={"class":"item_poster"})
    movie_posters = parent.find_all(class_='box_boxoffice')
    rank = 1

    wb = xl.Workbook()
    ws_rank = wb.create_sheet("영화 순위")
    ws_url = wb.create_sheet("URL")

    for movie_rank in movie_ranks:
        title = movie_rank.find("strong").get_text()
        link =  "https://movie.daum.net" + movie_rank.a["href"]
        story = movie_rank.a.get_text()
        #print("{}.".format(rank), title, link, story)
        ws_rank.append(["{}위".format(rank), title, story, link])
        rank += 1

    for movie_poster in movie_posters:
        poster = movie_poster.find('img')
        poster_src = poster['src']
        #print(poster_src)
        ws_url.append([poster_src])

    wb.save('MovieRank.xlsx')


# 디스코드 봇 실행 코드

game = discord.Game("ㄹㅇ 도움요청")
bot = commands.Bot(command_prefix='ㄹㅇ ', status=discord.Status.online, activity=game)

@bot.event
async def on_ready():
    print('사용중인 봇 :', bot.user.name)
    print('정상적으로 작동중입니다.\n')
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command(aliases=['안녕', 'hi', '안녕하세요', 'ㅎㅇ'])
async def hello(ctx):
    random_num = random.randrange(1,15)
    if random_num >= 4:
        await ctx.send(f'{ctx.author.mention}님 안녕하세요!')
    elif random_num < 4: # 낮은 확률로 다른 인사
        await ctx.send(f'어이 {ctx.author.mention} 드디어 왔구만!')

@bot.command()
async def 도움요청(ctx):
    embed = discord.Embed(title='도움말', description='제작 by Seung_hoen', color = 0x00ff00)
    embed.add_field(name='1. 인사', value='ex) ㄹㅇ 안녕', inline=False)
    embed.add_field(name='2. 오늘의 운세', value='ex) ㄹㅇ 운세 <~띠>', inline=False)
    embed.add_field(name='3. 국내 코로나 현황', value='ex) ㄹㅇ 코로나', inline=False)
    embed.add_field(name='4. 이번주 영화 순위', value='ex) ㄹㅇ 영화', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 운세(ctx, *, text):
    crawl_daily_fortune() # 크롤링
    wb = xl.load_workbook('파일경로/fortune.xlsx') 
    sheet = wb[text]

    one_line = [sheet['A1'].value]
    year_line = []

    for data in sheet['A4':'B6']:
        for cell in data:
            year_line.append(cell.value)
    wb.close()

    embed = discord.Embed(title=text, description=one_line[0], color=0xffff00)
    embed.add_field(name=year_line[0], value=year_line[1], inline=False)
    embed.add_field(name=year_line[2], value=year_line[3], inline=False)
    embed.add_field(name=year_line[4], value=year_line[5], inline=False)
    embed.add_field(name='더 보기...', value='Link : https://unse.daily.co.kr/?p=zodiac', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 코로나(ctx):
    # 보건복지부 코로나 바이러스 정보사이트"
    covidSite = "http://ncov.mohw.go.kr/index.jsp"
    covidNotice = "http://ncov.mohw.go.kr"
    html = urlopen(covidSite)
    bs = BeautifulSoup(html, 'html.parser')
    latestupdateTime = bs.find('span', {'class': "livedate"}).text.split(',')[0][1:].split('.')
    statisticalNumbers = bs.findAll('span', {'class': 'num'})
    beforedayNumbers = bs.findAll('span', {'class': 'before'})

    #주요 브리핑 및 뉴스링크
    briefTasks = []
    mainbrief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
    for brf in mainbrief:
        container = []
        container.append(brf.text)
        container.append(covidNotice + brf['href'])
        briefTasks.append(container)
    print(briefTasks)

    # 통계수치
    statNum = []
    # 전일대비 수치
    beforeNum = []
    for num in range(7):
        statNum.append(statisticalNumbers[num].text)
    for num in range(4):
        beforeNum.append(beforedayNumbers[num].text.split('(')[-1].split(')')[0])

    totalPeopletoInt = statNum[0].split(')')[-1].split(',')
    totalPeopleDeathtoInt = statNum[3].split(')')[-1].split(',')
    tpInt = ''.join(totalPeopletoInt)
    tpDInt = ''.join(totalPeopleDeathtoInt)
    lethatRate = round((int(tpDInt) / int(tpInt)) * 100, 2)
    
    embed = discord.Embed(title="Covid-19 Virus Korea Status", description="",color=0x5CD1E5)
    embed.add_field(name="Data source : Ministry of Health and Welfare of Korea", value="http://ncov.mohw.go.kr/index.jsp", inline=False)
    embed.add_field(name="Latest data refred time",value="해당 자료는 " + latestupdateTime[0] + "월 " + latestupdateTime[1] + "일 "+latestupdateTime[2] +" 자료입니다.", inline=False)
    embed.add_field(name="확진환자(누적)", value=statNum[0].split(')')[-1]+"("+beforeNum[0]+")",inline=True)
    embed.add_field(name="완치환자(격리해제)", value=statNum[1] + "(" + beforeNum[1] + ")", inline=True)
    embed.add_field(name="치료중(격리 중)", value=statNum[2] + "(" + beforeNum[2] + ")", inline=True)
    embed.add_field(name="사망", value=statNum[3] + "(" + beforeNum[3] + ")", inline=True)
    embed.add_field(name="누적확진률", value=statNum[6], inline=True)
    embed.add_field(name="치사율", value=str(lethatRate) + " %",inline=True)
    embed.add_field(name="- 최신 브리핑 1 : " + briefTasks[0][0],value="Link : " + briefTasks[0][1],inline=False)
    embed.add_field(name="- 최신 브리핑 2 : " + briefTasks[1][0], value="Link : " + briefTasks[1][1], inline=False)
    embed.set_thumbnail(url="https://wikis.krsocsci.org/images/7/79/%EB%8C%80%ED%95%9C%EC%99%95%EA%B5%AD_%ED%83%9C%EA%B7%B9%EA%B8%B0.jpg")
    embed.set_footer(text='Helped by Hoplin.')
    await ctx.send("Covid-19 Virus Korea Status", embed=embed)

@bot.command()
async def 영화(ctx):
    movie_rank() # 크롤링
    wb = xl.load_workbook('파일경로/MovieRank.xlsx') 
    sheet1 = wb["영화 순위"]
    sheet3 = wb["URL"]
    rank = []
    poster = [sheet3['A1'].value]
    for data in sheet1['A1':'B19']:
        for cell in data:
            rank.append(cell.value)

    wb.close()
    
    embed = discord.Embed(title="박스오피스 영화 순위", description="현재 박스오피스 1위 ~ 10위 영화", color=0x00ffff)
    embed.add_field(name="==================================================", value="Link : https://movie.daum.net/ranking/boxoffice/weekly", inline=False)
    embed.add_field(name=rank[0], value=rank[1], inline=False)
    #embed.add_field(name="==================================================", value="ㅤ", inline=False)
    embed.add_field(name=rank[2], value=rank[3], inline=True)
    embed.add_field(name=rank[4], value=rank[5], inline=True)
    embed.add_field(name=rank[6], value=rank[7], inline=True)
    embed.add_field(name=rank[8], value=rank[9], inline=True)
    embed.add_field(name=rank[10], value=rank[11], inline=True)
    embed.add_field(name=rank[12], value=rank[13], inline=True)
    embed.add_field(name=rank[14], value=rank[15], inline=True)
    embed.add_field(name=rank[16], value=rank[17], inline=True)
    embed.add_field(name=rank[18], value=rank[19], inline=True)
    embed.add_field(name="==================================================", value="ㅤ", inline=False)
    embed.add_field(name='현재 1위 영화', value="1위 영화 보러가기 -----> {}".format(sheet1['D1'].value), inline=False)
    #embed.set_thumbnail(url=poster[0])
    embed.set_image(url=poster[0])
    
    await ctx.send(embed=embed)

bot.run('사용중인 봇 토큰')
