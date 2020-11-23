from backtest import BackTest
import pandas as pd

#매일 장이 끝난 후에 이 파일을 돌려야 백테스트를 위한 분봉데이터를 수집할 수 있음.
if __name__ == "__main__":
    #객체 생성
    backtest = BackTest()
    #통신 확인
    if backtest.InitPlusCheck() == False:
        exit()

    # 전체 코스피, 코스닥 코드 불러오기
    entire_code, entire_name = backtest.get_entire_code()
    # code = backtest.get_yesterday_highest()
    
    # # 어제 상한가 종목 및 날짜 불러오기
    # date_company = pd.DataFrame([[backtest.today,code]],columns=['내일날짜','상한가다음날'])

    # # 해당 분봉 데이터 업데이트
    # backtest.get_minute_stock(date_company, entire_code, int(backtest.today))

    # 특정 날짜 빼먹었을 때 데이터 축적
    code = ['A003495']
    specific_date = '20201117'
    date_company = pd.DataFrame([[specific_date,code]], columns = ['내일날짜','상한가다음날'])
    backtest.get_minute_stock(date_company, entire_code, int(specific_date))


    # 긴 기간을 구하고 싶을때
    # change = backtest.get_change(entire_code, 100)
    # date_company = backtest.date_company_extract(change)
    # backtest.get_minute_stock(date_company, entire_code, int(backtest.today))

    # time 수익률 계산 여러 밴드 설정
    # limit_list = [-0.02, -0.025, -0.03,-0.035,-0.04,-0.045,-0.05,-0.055]
    # my_dict = {}
    # for i in limit_list:
    #     target_time, profit = backtest.time_profit_extract(fromdate=20190513, lower_limit = i, starttime=901, priority=True, down=False)
    #     my_dict[i] = [target_time, profit]
    # print (my_dict)

 