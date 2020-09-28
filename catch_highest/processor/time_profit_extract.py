import pandas as pd
import numpy as np
import ast
import os
from tqdm import tqdm
import warnings
warnings.filterwarnings(action='ignore') 

#해당 폴더 들어가기 전까지의 본인의 path 설정
PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven'

#분봉 데이터 파일들을 모두 리스트에 넣기
file_list = os.listdir(PATH + "catch_highest/data/minute_stock_data/")
file_list.sort()
# if '.DS_Store' in file_list:
    file_list = file_list[1:]
else:
    None

#첫번째 파일인 20180912 네이처셀으로 우선 뼈대 구성
first_file_name = file_list[0][0:-4]
df = pd.read_csv(PATH + "catch_highest/data/minute_stock_data/" + file_list[0], usecols=['time','open'])
df.columns = ['time',first_file_name]
df[first_file_name] = df[first_file_name].astype('float') 
for i in range(1,df.shape[0]):
    value = round((df[first_file_name][i] - df[first_file_name][0]) / df[first_file_name][0],4)
    df[first_file_name][i] = value

#이전에 만든 파일 제외하고 나머지로 다시 파일리스트 구성, 데이터프레임 하나로 합치기
file_list = file_list[1:]
for file in tqdm(file_list):
    file = file[0:-4]
    test = pd.read_csv(PATH + "catch_highest/data/minute_stock_data/%s.csv" % file, usecols=['time','open'])
    test.columns = ['time',file]
    test[file] = test[file].astype('float') 
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

#첫번째 행에 수익률에 곱하기 자기자본 (ex. 100) 해서 틀 만들기
for i in range(df.shape[1]):
    df.iloc[i][1] = 100*(1+df.iloc[i][1])

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

#해당 파일은 csv 파일로 변환
df.to_csv(PATH + "catch_highest/data/final_result/profit_with_time_preferred_yes.csv", encoding='utf-8-sig')

#수익이 가장 극대화되는 시간대와 수익률
target_time = int(df.iloc[:,1:].max(axis=0).idxmax())
profit = round((df.iloc[:,1:].max(axis=0).max()/100),2)
print('가장 수익률이 극대화되는 시간은 ' + str(target_time) + '이며, 수익률은 대략 ' + str(profit) + '배 정도 됩니다.')

