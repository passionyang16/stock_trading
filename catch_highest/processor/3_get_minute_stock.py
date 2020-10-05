import win32com.client
import pandas as pd
from tqdm import tqdm
import time
import ast

PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven\\'

# 연결 여부 체크
objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
bConnect = objCpCybos.IsConnect
if (bConnect == 0):
    print("PLUS가 정상적으로 연결되지 않음.")
    exit()

# 저장된 파일을 불러서 코스피, 코스닥 종목들의 코드와 이름을 변수에 저장
df = pd.read_csv(PATH + "catch_highest/data/extracted_data/kospi_kosdaq_list.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

#na 값들은 제거하고 list 형태로 변환, 해당 변수에 저장
kospicode = df['kospicode'].dropna().tolist()
kospiname = df['kospiname'].dropna().tolist()
kospicode_entire = df['kospicode_entire'].dropna().tolist()
kospiname_entire = df['kospiname_entire'].dropna().tolist()
kosdaqcode = df['kosdaqcode'].dropna().tolist()
kosdaqname = df['kosdaqname'].dropna().tolist()

#코드 6자리 맞추기
kospicode = list(map(int, kospicode))
kosdaqcode = list(map(int, kosdaqcode))
kosdaqcode = list(map(str,kosdaqcode))

for i in range(len(kosdaqcode)):
    if len(kosdaqcode[i]) != 6:
        kosdaqcode[i] = kosdaqcode[i].zfill(6)
    
    kosdaqcode[i] = 'A' + kosdaqcode[i]

# 코스피 코스닥 합치기
integrated_code = kospicode_entire+kosdaqcode
integrated_name = kospiname_entire+kosdaqname

# 상따 목록 불러오기
df2 = pd.read_csv(PATH + "catch_highest/data/extracted_data/date_company_list.csv")
df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

for i in range(df2.shape[0]):
    df2['상한가'][i] = ast.literal_eval(df2['상한가'][i])

df2 = df2[['내일날짜', '상한가']]
df2.columns = ['상한가다음날', '상한가종목']

# #딕셔너리 형태로 저장
# SD_dic={}
# for i in range(len(df2)):
#     SD_dic[df2['상한가다음날'][i]]=df2['상한가종목'][i]

# stock_list_name = []
# stock_list_date = []
# for i in SD_dic.keys():
#     stock_list_date.append(i)
# for j in SD_dic.values():
#     stock_list_name.append(j)
stock_list_name = df2['상한가종목'].tolist()
stock_list_date = df2['상한가다음날'].tolist()


#분봉 데이터 뽑기
for i in tqdm(range(len(stock_list_date))):
    if stock_list_date[i] > 20180911:
        
        try:
            for j in range(len(stock_list_name[i])):
                times = []
                open_price = []
                high_price = []
                low_price = []
                close_price = []
                minute_volume = []
                print(stock_list_date[i])
                print(stock_list_name[i][j])
                print(integrated_code[integrated_name.index(stock_list_name[i][j])])
                code = (integrated_code[integrated_name.index(stock_list_name[i][j])])
                objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
                objStockChart.SetInputValue(0, code)  # 종목 코드 입력
                objStockChart.SetInputValue(1, ord('1'))  # Date 설정하여 데이터 받기
                objStockChart.SetInputValue(2, stock_list_date[i])  # todDte 까지
                objStockChart.SetInputValue(3, stock_list_date[i])  # fromDate 까지
                objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜, 시간, 시가,고가,저가,종가,거래량
                objStockChart.SetInputValue(6, ord('m'))  # '차트 주가 - 일간 차트 요청
                objStockChart.SetInputValue(9, ord('0'))  # 무수정주가 사용
                objStockChart.BlockRequest()
                length = objStockChart.GetHeaderValue(3)
                # print(length)
                for k in range(length):
                    day = objStockChart.GetDataValue(0, k)
                    time = objStockChart.GetDataValue(1, k)
                    if time < 1000:  # 0901 출력
                        time = '%04d' % objStockChart.GetDataValue(1, k)
                    open = objStockChart.GetDataValue(2, k)
                    high = objStockChart.GetDataValue(3, k)
                    low = objStockChart.GetDataValue(4, k)
                    close = objStockChart.GetDataValue(5, k)
                    # volume = objStockChart.GetDataValue(8, k)
                    times.append(time)
                    open_price.append(open)
                    high_price.append(high)
                    low_price.append(low)
                    close_price.append(close)

                times.reverse()
                open_price.reverse()
                high_price.reverse()
                low_price.reverse()
                close_price.reverse()
                df3 = pd.DataFrame(
                    {'time': times,
                     'open': open_price,
                     'high': high_price,
                     'low': low_price,
                     'close': close_price})
                df3.to_csv(PATH + "catch_highest/data/minute_stock_data/" + str(stock_list_date[i]) + '_' + integrated_name[integrated_code.index(code)] + '.csv',
                    encoding='utf-8-sig')
        except Exception as e:
            print("Error code: " + str(code))
            print("Error name: " + str(e))

    else:
        continue
