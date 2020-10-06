import win32com.client
import pandas as pd
from tqdm import tqdm
import time
import ast
import os
import warnings
import ctypes
warnings.filterwarnings(action='ignore') 

#API 연결상태 확인
def InitPlusCheck():

    g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')

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

if __name__ == "__main__":
    if InitPlusCheck() == False:
        exit()

