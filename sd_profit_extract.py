import pandas as pd
import numpy as np
from tqdm import tqdm
import ast

#상따 목록 불러오기
df = pd.read_csv("test_sangdda.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

for i in range(df.shape[0]):
    df['상한가'][i] = ast.literal_eval(df['상한가'][i])
    df['다음날수익률'][i] = ast.literal_eval(df['다음날수익률'][i])

#실제로 수익률 계산
for i in tqdm(range(df.shape[0]-1)):
    for j in df['상한가'][i]:
        company_df = pd.read_csv("stock_data/%s.csv" % j)
        company_df = company_df.loc[:, ~company_df.columns.str.contains('^Unnamed')]
        company_df = company_df.dropna(how='all')
        company_df = company_df.sort_values(by='date',ascending=True).reset_index(drop=True)
        match_index = company_df[company_df['date'].isin([df['date'][i]])].index
        tomorrow = company_df.iloc[match_index+1]
        today = company_df.iloc[match_index]
         
        # if temp.iloc[0][1] == temp.iloc[0][2] == temp.iloc[0][3] == temp.iloc[0][4] :
        # 쩜상 배제
        if tomorrow.iloc[0][1] > 1.29 * today.iloc[0][4]:
            pass
        # 거래정지 배제
        elif today.iloc[0][4] == tomorrow.iloc[0][1] == tomorrow.iloc[0][2] == tomorrow.iloc[0][3] == tomorrow.iloc[0][4] :
            pass
        else:
            if tomorrow.iloc[0][1]* 1.08 < tomorrow.iloc[0][2]:
                df['다음날수익률'][i].append(0.0775)
            elif tomorrow.iloc[0][1]*0.95 > tomorrow.iloc[0][3]:
                df['다음날수익률'][i].append(-0.0525)
            else:
                df['다음날수익률'][i].append(round(((tomorrow.iloc[0][4] - tomorrow.iloc[0][1]) / tomorrow.iloc[0][1]) - 0.0025,4))
 

# 빈 list 제거
for i in range(df.shape[0]):
    if df['다음날수익률'][i] == []:
        df = df.drop(i)

df.reset_index(drop=True,inplace=True)

# 복리 계산
df['내돈'] = [10000000 for x in range(len(df.index))]
for i in range(df.shape[0]-1):
    df['내돈'][i+1] = df['내돈'][i]*(sum(df['다음날수익률'][i])/len(df['다음날수익률'][i])+1)

#파일 추출
df.to_csv("인생끝.csv", encoding='utf-8-sig')