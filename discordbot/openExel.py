import pandas as pd
import openpyxl as xl

"""
def daily_fortune(animal):
    df_sheet_index = pd.read_excel('C:/discordbot/fortune.xls', sheet_name=[animal])

    print('[', df_sheet_index, ']')
daily_fortune('말띠')
"""

def daily_fortune(animal):
    wb = xl.load_workbook('C:/discordbot/fortune.xlsx') 
    sheet = wb[animal]

    one_line  = []
    year_line = []

    # A1 데이터를 가져오는 방법 
    one_line = sheet['A1'].value

    # A1 부터, B1 데이터까지 가져오기 
    for data in sheet['A4':'B6']:
        for cell in data:
            year_line.append(cell.value)

    print(one_line)
    print(year_line)
    wb.close()

animal = input('')
daily_fortune(animal)
