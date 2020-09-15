import win32com.client
from PyQt5.QtWidgets import *
import ctypes
from datetime import datetime
import time

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

class Kodex200:
    def __init__(self):
        # 연결 여부 체크
        if (g_objCpStatus.IsConnect == 0):
            print('PLUS가 정상적으로 연결되지 않음. ')
            return

        # 주문 초기화
        if (g_objCpTrade.TradeInit(0) != 0):
            print('주문 초기화 실패')
            return

        self.objStockMst = win32com.client.Dispatch('DsCbo1.StockMst') #주식 API 따오기
        self.acc = g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.accFlag = g_objCpTrade.GoodsList(self.acc, 1)  # 주식상품 구분
        self.objBuySell = win32com.client.Dispatch('CpTrade.CpTd0311')  # 매매 API 따오기
        self.objAmount = win32com.client.Dispatch('CpTrade.CpTdNew5331A') #수량 API 따오기
        self.objAccount = win32com.client.Dispatch('CpTrade.CpTd6033') #계좌 API 따오기
        # self.expectedPrice = win32com.client.Dispatch('DsCbo1.CpSvr9027') #예상체결 API 따오기

        return

    def Request(self):
        self.objStockMst.SetInputValue(0, 'A069500')
        self.objStockMst.BlockRequest()

        self.objAccount.SetInputValue(0, self.acc) # 계좌번호 불러오기
        self.objAccount.SetInputValue(1, self.accFlag[0]) #주식 불러오기
        self.objAccount.BlockRequest()

        #통신상태 확인
        if self.objStockMst.GetDibStatus() != 0:
            print('통신상태', self.objStockMst.GetDibStatus(), self.objStockMst.GetDibMsg1())
            return False

        curData = {}

        curData['계좌잔액'] = self.objAccount.GetHeaderValue(3)
        curData['코드'] = 'A069500'
        curData['종목명'] = g_objCodeMgr.CodeToName('A069500')
        curData['예상체결가'] = self.objStockMst.GetHeaderValue(55) # 예상체결가
        curData['현재가'] = self.objStockMst.GetHeaderValue(11)  # 현재가
        curData['시가'] = self.objStockMst.GetHeaderValue(13)  # 시가
        curData['전일종가'] = self.objStockMst.GetHeaderValue(10)  # 전일종가
        curData['거래량'] = self.objStockMst.GetHeaderValue(18)  # 거래량
        curData['상한가'] = g_objCodeMgr.GetStockMaxPrice('A069500') #상한가
        curData['하한가'] = g_objCodeMgr.GetStockMinPrice('A069500')  # 하한가
        # curData['주문가능수량'] = curData['계좌잔액'] / curData['상한가']

        # curData['주문가능수량'] = self.objAmount.GetHeaderValue(18)  # 10: 현금 주문 가능 금액 18: 현금 주문 가능 수량

        print(curData)

        return curData

    def sellOrder(self):
        curData = self.Request()

        # 현재가 통신
        if (self.Request() == False):
            w = QWidget()
            QMessageBox.warning(w, '오류', '현재가 통신 오류 발생/주문 중단')
            return

        print('신규 매도', '종목코드:', 'A069500', '가격:', curData['하한가'], '수량:', 3)

        self.objBuySell.SetInputValue(0, '1')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, 'A069500')  # 종목코드
        self.objBuySell.SetInputValue(4, 3)  # 수량
        self.objBuySell.SetInputValue(5, curData['하한가'])  # 주문단가

        # 주문 요청
        self.objBuySell.BlockRequest()

        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False

        return True

    def buyOrder(self):
        curData = self.Request()

        # 현재가 통신
        if (self.Request() == False):
            w = QWidget()
            QMessageBox.warning(w, '오류', '현재가 통신 오류 발생/주문 중단')
            return

        print('신규 매수', '종목코드:', 'A069500', '가격:', curData['상한가'], '수량:', 3)

        self.objBuySell.SetInputValue(0, '2')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, 'A069500')  # 종목코드
        self.objBuySell.SetInputValue(4, 3)  # 수량
        self.objBuySell.SetInputValue(5, curData['상한가'])  # 주문단가


        # 주문 요청
        self.objBuySell.BlockRequest()

        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False
        return True

class KodexInverse:
    def __init__(self):
        # 연결 여부 체크
        if (g_objCpStatus.IsConnect == 0):
            print('PLUS가 정상적으로 연결되지 않음. ')
            return

        # 주문 초기화
        if (g_objCpTrade.TradeInit(0) != 0):
            print('주문 초기화 실패')
            return

        self.objStockMst = win32com.client.Dispatch('DsCbo1.StockMst') #주식 API 따오기
        self.acc = g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.accFlag = g_objCpTrade.GoodsList(self.acc, 1)  # 주식상품 구분
        self.objBuySell = win32com.client.Dispatch('CpTrade.CpTd0311')  # 매매 API 따오기

        return

    def Request(self):
        self.objStockMst.SetInputValue(0, 'A114800')
        self.objStockMst.BlockRequest()

        #통신상태 확인
        if self.objStockMst.GetDibStatus() != 0:
            print('통신상태', self.objStockMst.GetDibStatus(), self.objStockMst.GetDibMsg1())
            return False

        curData = {}

        curData['코드'] = 'A114800'
        curData['종목명'] = g_objCodeMgr.CodeToName('A114800')
        curData['예상체결가'] = self.objStockMst.GetHeaderValue(55)  # 예상체결가
        curData['현재가'] = self.objStockMst.GetHeaderValue(11)  # 현재가
        curData['시가'] = self.objStockMst.GetHeaderValue(13)  # 시가
        curData['전일종가'] = self.objStockMst.GetHeaderValue(10)  # 전일종가
        curData['거래량'] = self.objStockMst.GetHeaderValue(18)  # 거래량
        curData['상한가'] = g_objCodeMgr.GetStockMaxPrice('A114800')  # 상한가
        curData['하한가'] = g_objCodeMgr.GetStockMinPrice('A114800')  # 하한가
        print(curData)

        return curData

    def sellOrder(self):
        curData = self.Request()

        # 현재가 통신
        if (self.Request() == False):
            w = QWidget()
            QMessageBox.warning(w, '오류', '현재가 통신 오류 발생/주문 중단')
            return

        print('신규 매도', '종목코드:', 'A114800', '가격:', curData['하한가'], '수량:', 13)

        self.objBuySell.SetInputValue(0, '1')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, 'A114800')  # 종목코드
        self.objBuySell.SetInputValue(4, 13)  # 수량
        self.objBuySell.SetInputValue(5, curData['하한가'])  # 주문단가

        # 주문 요청
        self.objBuySell.BlockRequest()

        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False

        return True

    def buyOrder(self):
        curData = self.Request()

        # 현재가 통신
        if (self.Request() == False):
            w = QWidget()
            QMessageBox.warning(w, '오류', '현재가 통신 오류 발생/주문 중단')
            return

        print('신규 매수', '종목코드:', 'A114800', '가격:', curData['상한가'], '수량:', 13)

        self.objBuySell.SetInputValue(0, '2')  # 1 매도 2 매수
        self.objBuySell.SetInputValue(1, self.acc)  # 계좌번호
        self.objBuySell.SetInputValue(2, self.accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.objBuySell.SetInputValue(3, 'A114800')  # 종목코드
        self.objBuySell.SetInputValue(4, 13)  # 수량
        self.objBuySell.SetInputValue(5, curData['상한가'])  # 주문단가


        # 주문 요청
        self.objBuySell.BlockRequest()

        rqStatus = self.objBuySell.GetDibStatus()
        rqRet = self.objBuySell.GetDibMsg1()
        print('통신상태', rqStatus, rqRet)
        if rqStatus != 0:
            return False
        return True




if __name__ == "__main__":
    if InitPlusCheck() == False:
        exit()

    buyStock = True
    sellStock = True
    execution = Kodex200()
    while buyStock:
        print('현재시간: ' +str(datetime.now().hour)+':'+str(datetime.now().minute)+':',str(datetime.now().second))
        curData = execution.Request()
        time.sleep(0.5)
        if (str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)) == '9:15:2':
            if curData['전일종가'] <= curData['예상체결가']:
                execution = Kodex200()
            else:
                execution = KodexInverse()
            execution.buyOrder()
            buyStock = False

    curData = execution.Request()
    if curData['전일종가'] <= curData['예상체결가']:
        execution = Kodex200()
    else:
        execution = KodexInverse()

    while sellStock:
        print('현재시간: ' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ':', str(datetime.now().second))
        curData = execution.Request()
        time.sleep(0.5)
        if curData['종목명'] == 'KODEX 200' :
            if (curData['현재가'] <= (curData['시가'] - 40)) | (curData['현재가'] >= (curData['시가'] + 110)) :  
                execution.sellOrder()
                sellStock = False
        elif curData['종목명'] == 'KODEX 인버스' :
            if (curData['현재가'] <= (curData['시가'] - 20)) | (curData['현재가'] >= (curData['시가'] + 25)) :
                execution.sellOrder()
                sellStock = False


