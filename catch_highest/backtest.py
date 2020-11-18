import sys
from PyQt5.QtWidgets import *
import ctypes
import win32com.client
import pandas as pd
import os
import json
import time
from tqdm import tqdm
from datetime import datetime
import ast
import warnings
import numpy as np
warnings.filterwarnings(action='ignore') 

class BackTest:
    def __init__(self):
        self.PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven\\'
        self.g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
        self.g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
        self.objRq = win32com.client.Dispatch("CpSysDib.CssStgFind")
        self.objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.today = datetime.today().strftime("%Y%m%d")
        return

    def InitPlusCheck(self):
        # 프로세스가 관리자 권한으로 실행 여부
        if ctypes.windll.shell32.IsUserAnAdmin():
            print('정상: 관리자권한으로 실행된 프로세스입니다.')
        else:
            print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
            return False
        # 연결 여부 체크
        if (self.g_objCpStatus.IsConnect == 0):
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False
        # 주문 관련 초기화
        ret = self.g_objCpTrade.TradeInit(0)
        if (ret != 0):
            print("주문 초기화 실패, 오류번호 ", ret)
            return False
        return True

    def get_entire_code(self):
        with open(self.PATH + "catch_highest/data/extracted_data/kospi_list.json") as kospi_file:
            kospi_data = json.load(kospi_file)

        with open(self.PATH + "catch_highest/data/extracted_data/kosdaq_list.json") as kosdaq_file:
            kosdaq_data = json.load(kosdaq_file)
        
        kospi_data.update(kosdaq_data)

        return list(kospi_data.keys()), list(kospi_data.values())

    def get_change(self, entire_code, data_num):
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
                self.objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
                self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
                self.objStockChart.SetInputValue(4, data_num)  # 최근 1500일 치
                self.objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
                self.objStockChart.SetInputValue(6, ord('D'))  # '차트 주가 - 일간 차트 요청
                self.objStockChart.SetInputValue(9, ord('0'))  # 수정주가 사용
                self.objStockChart.BlockRequest()
                length = self.objStockChart.GetHeaderValue(3)

                for i in range(length):
                    day = self.objStockChart.GetDataValue(0, i)
                    close = self.objStockChart.GetDataValue(4, i)
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
                df[self.g_objCodeMgr.CodeToName(code)] = change_close
            except:
                print("Error:" + str(code))

        df.to_csv(self.PATH + "catch_highest/data/extracted_data/{today}_stockchange_{data_num}days_before.csv".format(today=self.today, data_num=data_num), encoding='utf-8-sig')

        return df

    def date_company_extract(self, change):
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
        
        change.to_csv(self.PATH + "catch_highest/data/extracted_data/{today}_date_company_list.csv".format(today=self.today), encoding="utf-8-sig")

        return change

    def get_minute_stock(self, date_company, entire_code, fromdate):
        date_company.columns = ['상한가다음날', '상한가종목']
        stock_list_name = date_company['상한가종목'].tolist()
        stock_list_date = date_company['상한가다음날'].tolist()

        #분봉 데이터 뽑기
        for i in tqdm(range(len(stock_list_date))):
            if int(stock_list_date[i]) >= fromdate:
                try:
                    for j in range(len(stock_list_name[i])):
                        times = []
                        open_price = []
                        high_price = []
                        low_price = []
                        close_price = []
                        minute_volume = []
                        code = stock_list_name[i][j]
                        self.objStockChart.SetInputValue(0, code)  # 종목 코드 입력
                        self.objStockChart.SetInputValue(1, ord('1'))  # Date 설정하여 데이터 받기
                        self.objStockChart.SetInputValue(2, stock_list_date[i])  # todDte 까지
                        self.objStockChart.SetInputValue(3, stock_list_date[i])  # fromDate 까지
                        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜, 시간, 시가,고가,저가,종가,거래량
                        self.objStockChart.SetInputValue(6, ord('m'))  # '차트 주가 - 일간 차트 요청
                        self.objStockChart.SetInputValue(9, ord('0'))  # 무수정주가 사용
                        self.objStockChart.BlockRequest()
                        length = self.objStockChart.GetHeaderValue(3)
                        # print(length)
                        for k in range(length):
                            day = self.objStockChart.GetDataValue(0, k)
                            time = self.objStockChart.GetDataValue(1, k)
                            if time < 1000:  # 0901 출력
                                time = '%04d' % self.objStockChart.GetDataValue(1, k)
                            open = self.objStockChart.GetDataValue(2, k)
                            high = self.objStockChart.GetDataValue(3, k)
                            low = self.objStockChart.GetDataValue(4, k)
                            close = self.objStockChart.GetDataValue(5, k)
                            # volume = self.objStockChart.GetDataValue(8, k)
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
                        df3 = pd.DataFrame({'time': times, 'open': open_price, 'high': high_price, 'low': low_price,'close': close_price}, columns = ['time','open','high','low','close'])
                        df3.to_csv(self.PATH + "catch_highest/data/minute_stock_data/" + str(stock_list_date[i]) + '_'+ self.g_objCodeMgr.CodeToName(code) + '.csv',
                            encoding='utf-8-sig')
                except Exception as e:
                    print("Error code: " + str(code))
                    print("Error name: " + str(e))

            else:
                continue

    def time_profit_extract(self, fromdate, todate, lower_limit, starttime = 0, priority = False, down = False):
        
        #분봉 데이터 파일들을 모두 리스트에 넣기
        file_list = os.listdir(self.PATH + "catch_highest/data/minute_stock_data/")
        file_list.sort()
        if '.DS_Store' in file_list:
            file_list = file_list[1:]
        else:
            None
        # 숫자로 실행할때
        # file_list.reverse()
        # file_list = file_list[0:num]
        # file_list.sort()

        #처음날짜
        for i in range(len(file_list)):
            if file_list[i].startswith(str(fromdate)):
                file_list = file_list[i:]
                break
        #끝날짜
        for i in reversed(range(len(file_list))):
            if file_list[i].startswith(str(todate)):
                file_list = file_list[:i+1]
                break
        
        # 우선주만 보자
        if priority is True:
            new_file_list = []
            for i in range(len(file_list)):
                if file_list[i].endswith('우.csv') or file_list[i].endswith('우B.csv') or file_list[i].endswith('우C.csv'):
                    new_file_list.append(file_list[i])
            file_list = new_file_list

        #하락장일 때만 보자
        if down is True:
            df = pd.read_csv(self.PATH + "catch_highest/data/extracted_data/kosdaq_150.csv", usecols = ['date','open','close'])
            array = []
            for i in range(df.shape[0]-1):
                if df['open'][i] < df['close'][i+1]:
                    array.append(df['date'][i])
            array = list(map(str, array))
            new_file_list = []
            for i in range(len(file_list)):
                if file_list[i][0:8] in array:
                    new_file_list.append(file_list[i])
            file_list = new_file_list

        #데이터 모두 합치기
        df = pd.read_csv(self.PATH + "catch_highest/data/extracted_data/only_time.csv", usecols = ['time'])
        for i in range(df.shape[0]):
            if df['time'][i] == starttime:
                df = pd.DataFrame(df['time'][i:]).reset_index(drop=True)
                break

        for file in tqdm(file_list):
            file = file[0:-4]
            test = pd.read_csv(self.PATH + "catch_highest/data/minute_stock_data/%s.csv" % file, usecols=['time','open'])
            test.columns = ['time',file]
            test[file] = test[file].astype('int')
            # 단일가 거래 거르고
            if test.shape[0] < 50:
                continue
            # 동전주 거르고
            if len(str(test[file][0])) == 3:
                continue
                
            df = pd.merge(df,test, on='time', how = 'left')
            # 중간중간 vi 걸린 것들은 다음값으로 채워주고
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
                value = round((df[file][j] - df[file][0]) / df[file][0],4) - 0.0025
                if value <= lower_limit:
                    df[file][j:] = value
                    break
                else:
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

        df.to_csv(self.PATH + 'catch_highest/data/final_result/{fromdate}_{todate}_{lower_limit}_company_profit_with_time.csv'.format(fromdate = fromdate, todate=todate, lower_limit=lower_limit), encoding='utf-8-sig')

        for i in range(df.shape[0]):
            df['date'][i] = df['time'][i][0:8]
            df['company'][i] = df['time'][i][9:]

        cols = df.columns.tolist()
        cols = [cols[-2]] + cols[1:-2]
        df = df.reindex(columns=cols)

        #날짜별 기업들의 수익률 평균내기
        df = df.groupby('date').mean().reset_index()
        
        df.to_csv(self.PATH + 'catch_highest/data/final_result/{fromdate}_{todate}_{lower_limit}_only_mean_profit_with_time.csv'.format(fromdate = fromdate, todate=todate, lower_limit=lower_limit), encoding='utf-8-sig')

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
        df.to_csv(self.PATH + 'catch_highest/data/final_result/{fromdate}_{todate}_{lower_limit}_profit_with_time.csv'.format(fromdate = fromdate, todate=todate, lower_limit=lower_limit), encoding='utf-8-sig')

        #수익이 가장 극대화되는 시간대와 수익률
        df = pd.DataFrame(df.iloc[-1])
        df = df.T
        target_time = int(df.iloc[:,1:].max(axis=0).idxmax())
        profit = round((df.iloc[:,1:].max(axis=0).max()/100),2)
        print('가장 수익률이 극대화되는 시간은 ' + str(target_time) + '이며, 수익률은 대략 ' + str(profit) + '배 정도 됩니다.')
        return target_time, profit

    def get_yesterday_highest(self):
            
        self.objRq.SetInputValue(0, 'nyHoIn7oTgSILXpSOTqkuQ')  # 전략 id 요청
        self.objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = self.objRq.GetDibStatus()
        if rqStatus != 0:
            rqRet = self.objRq.GetDibMsg1()
            print("통신상태", rqStatus, rqRet)

        cnt = self.objRq.GetHeaderValue(0)  # 0 - (long) 검색된 결과 종목 수

        code = []
        name = []

        for i in range(cnt):
            code.append(self.objRq.GetDataValue(0, i))
            name.append(self.g_objCodeMgr.CodeToName(code[i]))

        print(code)
        print(name)
        return code

if __name__ == "__main__":
    #객체 생성
    backtest = BackTest()
    # #통신 확인
    # if backtest.InitPlusCheck() == False:
    #     exit()

    target_time, profit = backtest.time_profit_extract(fromdate=202009, todate = 202011, lower_limit = -3, starttime=901, priority=True, down=False)