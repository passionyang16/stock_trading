import win32com.client
import pandas as pd
from tqdm import tqdm
import time

PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven\\'

# 연결 여부 체크
objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
bConnect = objCpCybos.IsConnect
if (bConnect == 0):
    print("PLUS가 정상적으로 연결되지 않음.")
    exit()

integrated_code = ['A005930','A005380']
integrated_name = ['삼성전자', '현대차']


# 데이터 갯수 설정
data_num = 365
# 차트 객체 구하기
for code in tqdm(integrated_code):
    # 리스트 할당
    days = []
    close_price = []
    # change_close = []
    high_price = []
    open_price = []
    low_price = []
    # 데이터 불러오기
    time.sleep(0.1)
    try:
        objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
        objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
        objStockChart.SetInputValue(4, data_num)  # 최근 100일 치
        objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
        objStockChart.SetInputValue(6, ord('D'))  # '차트 주가 - 일간 차트 요청
        objStockChart.SetInputValue(9, ord('0'))  # 수정주가 사용
        objStockChart.BlockRequest()
        length = objStockChart.GetHeaderValue(3)

        #각 날짜별로 (?)
        for i in range(length):
            day = objStockChart.GetDataValue(0, i)
            open = objStockChart.GetDataValue(1, i)
            high = objStockChart.GetDataValue(2, i)
            low = objStockChart.GetDataValue(3, i)
            close = objStockChart.GetDataValue(4, i)
            vol = objStockChart.GetDataValue(5, i)
            days.append(day)
            close_price.append(close)
            low_price.append(low)
            open_price.append(open)
            high_price.append(high)

        df = pd.DataFrame({'date': days, 'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price},
        columns = ['date','open','high','low','close'])
        
        df.to_csv(PATH + "catch_highest/data/" + integrated_name[integrated_code.index(code)] + '.csv',
                    encoding='utf-8-sig')
    
    except Exception as e:
        print("Error code: " + str(code))
        print("Error name: " + str(e))
