from bs4 import BeautifulSoup
import requests     # 웹사이트에 접속
import openpyxl
import pandas as pd

def crawl_daily_fortune():
    url = 'https://unse.daily.co.kr/?p=zodiac'

    res = requests.get(url)

    soup = BeautifulSoup(res.text, 'html.parser')

    # 1. 내가 찾고자 하는 데이터를 포함하는 가장 근접한 부모
    parent = soup.select_one('#card')

    # 2. 부모 밑에 있는 자식 요소
    children = parent.select('ul')      # select: 여러개의 요소 / select_one: 가장 첫번째 요소

    wb = openpyxl.Workbook()

    children = parent.select('ul')      # select: 여러개의 요소 / select_one: 가장 첫번째 요소
    for i in children:
        lis = i.select('li')
        for n, li in enumerate(lis):
            if n == 0:
                animal = li.select_one('div > b').get_text()    # 태그 중 텍스트 추출
                total = li.select_one('div > p').get_text()
                print(animal, total)
                print()
                ws = wb.create_sheet(animal+'띠')    # animal 이름으로 시트 생성
                ws.append([total])    
            else:
                year = li.select_one('span').get_text()
                luck = li.select_one('p').get_text()
                print(year, luck)
                print()
                ws.append([year, luck])

    wb.save('fortune.xls')
