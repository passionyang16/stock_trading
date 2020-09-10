import pandas as pd
import numpy as np
from tqdm import tqdm
import ast

# 데이터프레임 만들기
# 다음문장에 해당 파일 집어넣기
df = pd.read_csv("change.csv", encoding = 'utf8', header=None)
df = df.iloc[0:df.shape[0]-1,1:]
df['상한가'] = [list() for x in range(len(df.index))]
df['다음날수익률'] = [list() for x in range(len(df.index))]

#상한가 종목 찾기
#상한가 범위 설정 가능
for i in tqdm(range(1,df.shape[0])):
    for j in range(2,df.shape[1]-1):
        if 29.3 < float(df.iloc[i][j]) <= 30:
            df['상한가'][i].append(df.iloc[0][j])

#빈 list는 삭제하고 유의미한 df만 남기기
df = df.reset_index()
df = df.loc[:,[1,'상한가','다음날수익률']]

for i in range(df.shape[0]):
    if df['상한가'][i] == []:
        df = df.drop(i)


df.reset_index(drop=True,inplace=True)
df = df.rename(columns={1:'date'})
df['date'] = df['date'].apply(pd.to_numeric)
df = df.sort_values(by='date',ascending=True).reset_index(drop=True)


# 파일 추출
df.to_csv("date_company_list.csv", encoding="utf-8-sig")