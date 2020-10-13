import win32com.client
import ctypes
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import time
from PyQt5.QtWidgets import *


g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')

#기본 세팅
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

class CatchHighest:
    def __init__(self):
        self.objStockMst = win32com.client.Dispatch('DsCbo1.StockMst') #주식 API 따오기
        self.acc = g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.accFlag = g_objCpTrade.GoodsList(self.acc, 1)  # 주식상품 구분
        self.objBuySell = win32com.client.Dispatch('CpTrade.CpTd0311')  # 매매 API 따오기
        self.objAmount = win32com.client.Dispatch('CpTrade.CpTdNew5331A') #수량 API 따오기
        self.objAccount = win32com.client.Dispatch('CpTrade.CpTd6033') #계좌 API 따오기
        # self.yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d') #어제 날짜 찾기
        self.yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d') #어제 날짜 찾기
        return

    #전날 상한가 종목을 return 하는 함수
    def get_yesterday_highest(self):
        #날짜 설정
        print(self.yesterday)
        url = 'https://puzizig.com/programs/stock_upper_limit/date/' + self.yesterday
        #URL 접근
        request = requests.get(url)
        soup = BeautifulSoup(request.content,'html.parser')
        selected = soup.select('body > div > div > div.col-md-8.mt-3 > div:nth-child(4)')
        #코드 및 종목 찾기
        code = []
        company = []
        info_html = selected[0].find_all('div',{'class':'d-flex align-items-center mb-2'})
        for info in info_html:
            code.append('A' + info.find('span',{'class':'badge badge-secondary badge-pill mr-2'}).text)
            company.append(info.find('a').text)
        
        #가격 찾아서 동전주는 깔끔하게 제거
        table_html = selected[0].find_all('div',{'class':'col-md-6 col-lg-3'})
        price = [table.text[5:].replace(',','') for table in table_html if table.text.startswith('현재가')]
        # 거래량 데이터 추후 단일가 제거시 사용 가능
        # amount = [table.text[5:].replace(',','') for table in table_html if table.text.startswith('거래량')]
        for i in reversed(range(len(code))):
            if len(price[i]) <= 3:
                code.pop(i)
        
        print("어제 상한가 종목은: ", company)
        return code

    #데이터를 받아서 모아놓는 함수
    def request(self, code, num):
        #통신상태 확인
        if self.objStockMst.GetDibStatus() != 0:
            print('통신상태', self.objStockMst.GetDibStatus(), self.objStockMst.GetDibMsg1())
            return False
        
        #해당 종목 연결
        self.objStockMst.SetInputValue(0, code)
        self.objStockMst.BlockRequest()

        #계좌 연결
        self.objAccount.SetInputValue(0, self.acc) # 계좌번호 불러오기
        self.objAccount.SetInputValue(1, self.accFlag[0]) #주식 불러오기
        self.objAccount.BlockRequest()

        #데이터 쌓기
        curData = {}
        curData['예수금'] = self.objAccount.GetHeaderValue(9)
        curData['코드'] = code
        curData['종목명'] = g_objCodeMgr.CodeToName(code)
        curData['전일종가'] = self.objStockMst.GetHeaderValue(10)  # 전일종가
        #추후 사용예정
        #curData['예상체결가'] = self.objStockMst.GetHeaderValue(55) # 예상체결가
        curData['매수금액'] = curData['예수금'] // num
        curData['수량'] = curData['매수금액'] // curData['전일종가']
        
        return curData
    
    
    def buyOrder(self, curData):
        
        #원하는 주문 방식
        self.objBuySell.SetInputValue(0, '2')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, curData['코드'])  # 종목코드
        self.objBuySell.SetInputValue(4, curData['수량'])  # 수량
        self.objBuySell.SetInputValue(5, 0)  # 주문단가
        self.objBuySell.SetInputValue(7, "0") # 주문 조건 구분 코드 - 0:기본 1:IOC 2:FOK
        self.objBuySell.SetInputValue(8, "03")


        # 주문 요청
        self.objBuySell.BlockRequest()

        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False

        print('신규 매수', '종목명:', curData['종목명'], '수량:', curData['수량'])

        return True


    def sellOrder(self, code, amount):


        #원하는 주문 방식
        self.objBuySell.SetInputValue(0, '1')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, code)  # 종목코드
        self.objBuySell.SetInputValue(4, amount)  # 수량
        self.objBuySell.SetInputValue(5, 0)  # 주문단가
        self.objBuySell.SetInputValue(7, "0") # 주문 조건 구분 코드 - 0:기본 1:IOC 2:FOK
        self.objBuySell.SetInputValue(8, "03")


        # 주문 요청
        self.objBuySell.BlockRequest()
        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False

        print('신규 매도', '종목명:', g_objCodeMgr.CodeToName(code), '수량:', amount)

        return True


if __name__ == "__main__":
    if InitPlusCheck() == False:
        exit()

    #객체 설정
    catchhighest = CatchHighest()
    codes = catchhighest.get_yesterday_highest()
    buyStock = True
    sellStock = True
    stock_dict = {}
    #매수 주문
    while buyStock:
        current_time = str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)
        if current_time == '8:59:0':
            for code in codes:
                curData = catchhighest.request(code, len(codes))
                print(curData)
                catchhighest.buyOrder(curData)
                stock_dict[code] = curData['수량']
            buyStock = False

    print(stock_dict)
    #매도 주문
    while sellStock:
        current_time = str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)
        print(current_time)
        if current_time == '9:7:0':
            for key,value in stock_dict.items():
                catchhighest.sellOrder(key, value)
            sellStock = False
