import sys
from PyQt5.QtWidgets import *
import ctypes
import win32com.client
import pandas as pd
import os
import json
import time
from tqdm import tqdm
from datetime import date
import ast
import warnings
import numpy as np
warnings.filterwarnings(action='ignore') 


#기본 세팅
PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven\\'
today = str(date.today()).replace('-','')
g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')

def InitPlusCheck():
    # 프로세스가 관리자 권한으로 실행 여부
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('정상: 관리자권한으로 실행된 프로세스입니다.')
    else:
        print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        return False
    # 연결 여부 체크
    if (g_objCpStatus.IsConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        return False
    # 주문 관련 초기화
    ret = g_objCpTrade.TradeInit(0)
    if (ret != 0):
        print("주문 초기화 실패, 오류번호 ", ret)
        return False
    return True

def get_entire_code():
    with open(PATH + "catch_highest/data/extracted_data/kospi_list.json") as kospi_file:
        kospi_data = json.load(kospi_file)

    with open(PATH + "catch_highest/data/extracted_data/kosdaq_list.json") as kosdaq_file:
        kosdaq_data = json.load(kosdaq_file)
    
    kospi_data.update(kosdaq_data)

    return list(kospi_data.keys()), list(kospi_data.values())

def get_day_stock(data_num):
    #코스피, 코스닥 종목 불러오기
    entire_code, entire_name = get_entire_code()

    # 날짜 데이터프레임 작성을 위해
    startpoint = 0

    # 차트 객체 구하기
    for code in tqdm(entire_code):
        # 리스트 할당
        days = []
        close_price = []
        change_close = []
        # 데이터 불러오기
        try:
            objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
            objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
            objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
            objStockChart.SetInputValue(4, data_num)  # 최근 1500일 치
            objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
            objStockChart.SetInputValue(6, ord('D'))  # '차트 주가 - 일간 차트 요청
            objStockChart.SetInputValue(9, ord('0'))  # 수정주가 사용
            objStockChart.BlockRequest()
            length = objStockChart.GetHeaderValue(3)

            for i in range(length):
                day = objStockChart.GetDataValue(0, i)
                close = objStockChart.GetDataValue(4, i)
                days.append(day)
                close_price.append(close)

            # 불러오려는 일자 이후에 상장한 기업에 대한 변수처리
            if len(close_price) < data_num:
                for i in range(data_num - len(close_price)):
                    close_price.append(int(1))  # 0 넣으면 chang_close 0으로 나눠버림

            # 종가 변동성 계산
            for i in range(len(close_price) - 1):
                change_close.append(((close_price[i] - close_price[i + 1]) / close_price[i + 1]) * 100)
            change_close.insert(len(close_price) - 1, '0')  # 첫날 변동률 0 처리

            # 데이터프레임 맨 처음 날짜 입력, 이후 열 추가
            if startpoint == 0:
                df = pd.DataFrame()
                df['date'] = days
                startpoint += 1  # 날짜 중복 제거
            df[entire_name[entire_code.index(code)]] = change_close
        except:
            print("Error:" + str(code))

    df.to_csv(PATH + "catch_highest/data/extracted_data/{today}_stockchange_{data_num}days_before.csv".format(today=today, data_num=data_num), encoding='utf-8-sig')

    return df

def date_company_extract(change):
    change['내일날짜'] = [0 for x in range(len(change.index))]
    change['상한가'] = [list() for x in range(len(change.index))]

    #상한가 종목 찾기
    #상한가 범위 설정 가능
    for i in tqdm(range(1,change.shape[0])):
        for j in range(2,change.shape[1]-1):
            if 29.3 < float(change.iloc[i][j]) <= 30:
                change['상한가'][i].append(change.iloc[0][j])

    #빈 list는 삭제하고 유의미한 df만 남기기
    change = change.reset_index()
    change = change.loc[:,[1,'상한가','내일날짜']]

    for i in range(change.shape[0]):
        if change['상한가'][i] == []:
            change = change.drop(i)


    change.reset_index(drop=True,inplace=True)
    change = change.rename(columns={1:'date'})
    change['date'] = change['date'].apply(pd.to_numeric)
    change = change.sort_values(by='date',ascending=True).reset_index(drop=True)

    for i in tqdm(range(0,change.shape[0]-1)):
        change['내일날짜'][i] = change.iloc[i+1][0]
    
    change.to_csv(PATH + "catch_highest/data/extracted_data/{today}_date_company_list.csv".format(today=today), encoding="utf-8-sig")

    return change

def get_minute_stock(date_company, fromdate):
    date_company = date_company[['내일날짜', '상한가']]
    date_company.columns = ['상한가다음날', '상한가종목']

    stock_list_name = date_company['상한가종목'].tolist()
    stock_list_date = date_company['상한가다음날'].tolist()

    #코스피, 코스닥 종목 부르기
    entire_code, entire_name = get_entire_code()

    #분봉 데이터 뽑기
    for i in tqdm(range(len(stock_list_date))):
        if stock_list_date[i] > fromdate:
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
                    print(entire_code[entire_name.index(stock_list_name[i][j])])
                    code = (entire_code[entire_name.index(stock_list_name[i][j])])
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
                    df3 = pd.DataFrame({'time': times, 'open': open_price, 'high': high_price, 'low': low_price,'close': close_price})
                    df3.to_csv(PATH + "catch_highest/data/minute_stock_data/" + str(stock_list_date[i]) + '_' + entire_name[entire_code.index(code)] + '.csv',
                        encoding='utf-8-sig')
            except Exception as e:
                print("Error code: " + str(code))
                print("Error name: " + str(e))

        else:
            continue




def time_profit_extract(start_date, end_date):
    
    #분봉 데이터 파일들을 모두 리스트에 넣기
    file_list = os.listdir(PATH + "catch_highest/data/minute_stock_data/")
    file_list.sort()
    if '.DS_Store' in file_list:
        file_list = file_list[1:]
    else:
        None

    
    #처음날짜
    for i in range(len(file_list)):
        if file_list[i].startswith(start_date):
            file_list = file_list[i:]
            break
    #끝날짜
    for i in reversed(range(len(file_list))):
        if file_list[i].startswith(end_date):
            file_list = file_list[:i+1]
            break

    #뼈대 구성
    df = pd.read_csv(PATH + "catch_highest/data/extracted_data/only_time.csv", usecols = ['time'])

    for file in tqdm(file_list):
        file = file[0:-4]
        test = pd.read_csv(PATH + "catch_highest/data/minute_stock_data/%s.csv" % file, usecols=['time','open'])
        test.columns = ['time',file]
        test[file] = test[file].astype('int')
        if test.shape[0] < 50:
            continue
        if len(str(test[file][0])) == 3:
            continue
            
        df = pd.merge(df,test, on='time', how = 'left')

        for i in range(df.shape[0]):
            if np.isnan(df[file][i]):
                index = i 
                stopping = True
                try:
                    while stopping:
                        if np.isnan(df[file][index+1]):
                            index += 1
                        else:
                            valid = df[file][index+1]
                            stopping = False
                    df[file][i] = valid
                except:
                    continue
        
        for j in range(1,df.shape[0]):
            value = round((df[file][j] - df[file][0]) / df[file][0],4)
            df[file][j] = value

    #해당 날짜에 값이 없는 경우에는 모두 0으로 대체
    df = df.fillna(0)

    #기준이 되는 0901 지우고 데이터 행-열 변환
    df = df.iloc[1:,:].T.reset_index()
    df.columns = df.iloc[0]
    df = df.iloc[1:,:].reset_index(drop=True)

    #날짜와 기업 자르고 다시 재정렬
    df['date'] = [str() for x in range(len(df.index))]
    df['company'] = [str() for x in range(len(df.index))]

    for i in range(df.shape[0]):
        df['date'][i] = df['time'][i][0:8]
        df['company'][i] = df['time'][i][9:]

    cols = df.columns.tolist()
    cols = [cols[-2]] + cols[1:-2]
    df = df.reindex(columns=cols)

    #날짜별 기업들의 수익률 평균내기
    df = df.groupby('date').mean().reset_index()

    # date와 나머지 열을 쪼개서 각각 temp, temp2에 저장
    temp = df.iloc[:,0]
    temp2 = df.iloc[:,1:]

    #숫자만 들어가 있는 temp2에서 복리 계산을 진행
    for j in tqdm(temp2.columns):
        temp2[j][0] = 100*(1+temp2[j][0])
        for i in range(1, temp2.shape[0]):
            temp2[j][i] = temp2[j][i-1] * (1+temp2[j][i])

    #이제 다시 쪼개진 데이터프레임들 결합
    df = pd.concat([temp,temp2],axis=1)
    df.to_csv(PATH + 'catch_highest/data/final_result/{start_date}_{end_date}_profit_with_time.csv'.format(start_date=start_date, end_date=end_date), encoding='utf-8-sig')

    #수익이 가장 극대화되는 시간대와 수익률
    target_time = int(df.iloc[:,1:].max(axis=0).idxmax())
    profit = round((df.iloc[:,1:].max(axis=0).max()/100),2)
    print('가장 수익률이 극대화되는 시간은 ' + str(target_time) + '이며, 수익률은 대략 ' + str(profit) + '배 정도 됩니다.')

if __name__ == "__main__":
    if InitPlusCheck() == False:
        exit()
    
    # change = get_day_stock(100)
    # date_company = date_company_extract(change)
    # get_minute_stock(date_company,20201001)
    time_profit_extract('20200901','20201027')
