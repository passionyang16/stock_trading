import sys
from PyQt5.QtWidgets import *
import win32com.client
import pandas as pd
import os

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')

# 2번 코드

objRq = win32com.client.Dispatch("CpSysDib.CssStgFind")
objRq.SetInputValue(0, 'nyHoIn7oTgSILXpSOTqkuQ')  # 전략 id 요청
objRq.BlockRequest()

# 통신 및 통신 에러 처리
rqStatus = objRq.GetDibStatus()
if rqStatus != 0:
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)


cnt = objRq.GetHeaderValue(0)  # 0 - (long) 검색된 결과 종목 수

SD_code = []
SD_name = []
for i in range(cnt):
    SD_code.append(objRq.GetDataValue(0, i))
    SD_name.append(g_objCodeMgr.CodeToName(SD_code[i]))

print(SD_code)
print(SD_name)