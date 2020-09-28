import win32com.client
import pandas as pd

PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven'

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

#혹시 몰라 float를 int로 변경
kospicode = list(map(int, kospicode))
kosdaqcode = list(map(int, kosdaqcode))


# 날짜 데이터프레임 작성을 위해
startpoint = 0
# 데이터 갯수 설정
data_num = 600

# 차트 객체 구하기
for code in kospicode_entire:
    # 리스트 할당
    days = []
    close_price = []
    change_close = []
    high_price = []
    open_price = []
    low_price = []
    # 데이터 불러오기
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, data_num)  # 최근 1500일 치
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord('D'))  # '차트 주가 - 일간 차트 요청
    objStockChart.SetInputValue(9, ord('0'))  # 수정주가 사용
    objStockChart.BlockRequest()
    length = objStockChart.GetHeaderValue(3)

    # print("날짜", "시가", "고가", "저가", "종가", "거래량")
    # print("빼기빼기==============================================-")

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
    # 불러오려는 일자 이후에 상장한 기업에 대한 변수처리
    if len(close_price) < data_num:
        for i in range(data_num - len(close_price)):
            close_price.append(int(1))  # 0 넣으면 chang_close 0으로 나눠버림
    print(kospiname_entire[kospicode_entire.index(code)])
    # print(len(close_price))
    # 종가 변동성 계산
    for i in range(len(close_price) - 1):
        change_close.append(((close_price[i] - close_price[i + 1]) / close_price[i + 1]) * 100)
    change_close.insert(len(close_price) - 1, '0')  # 첫날 변동률 0 처리
    # 데이터프레임 맨 처음 날짜 입력, 이후 열 추가
    if startpoint == 0:
        df = pd.DataFrame()
        df['date'] = days
        startpoint += 1  # 날짜 중복 제거
    df[kospiname_entire[kospicode_entire.index(code)]] = change_close

df.to_csv(PATH + "catch_highest/data/extracted_data/change_kospi_entire.csv", encoding='utf-8-sig')
# df.reset_index(drop=True)
print(df.index)
