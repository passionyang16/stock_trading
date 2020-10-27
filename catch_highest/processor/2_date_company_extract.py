import pandas as pd
import numpy as np
from tqdm import tqdm
import ast
import warnings
warnings.filterwarnings(action='ignore') 


#해당 폴더 들어가기 전까지의 본인의 path 설정
PATH = 'c:\\Users\\passi\\Desktop\\programming\\stair_to_heaven\\'

# 데이터프레임 만들기
# 다음문장에 해당 파일 집어넣기
df = pd.read_csv(PATH + "catch_highest/data/extracted_data/20201027_stockchange_100days_before.csv", encoding = 'utf8', header=None)
df = df.iloc[0:df.shape[0]-1,1:]
df['내일날짜'] = [0 for x in range(len(df.index))]
df['상한가'] = [list() for x in range(len(df.index))]



#상한가 종목 찾기
#상한가 범위 설정 가능
for i in tqdm(range(1,df.shape[0])):
    for j in range(2,df.shape[1]-1):
        if 29.3 < float(df.iloc[i][j]) <= 30:
            df['상한가'][i].append(df.iloc[0][j])

#빈 list는 삭제하고 유의미한 df만 남기기
df = df.reset_index()
df = df.loc[:,[1,'상한가','내일날짜']]

for i in range(df.shape[0]):
    if df['상한가'][i] == []:
        df = df.drop(i)


df.reset_index(drop=True,inplace=True)
df = df.rename(columns={1:'date'})
df['date'] = df['date'].apply(pd.to_numeric)
df = df.sort_values(by='date',ascending=True).reset_index(drop=True)

for i in tqdm(range(0,df.shape[0]-1)):
    df['내일날짜'][i] = df.iloc[i+1][0]

# for i in tqdm(range(df.shape[0]-1)):
#     for j in df['상한가'][i]:
#         company_df = pd.read_csv(PATH + "catch_highest/data/day_stock_data/%s.csv" % j)
#         company_df = company_df.loc[:, ~company_df.columns.str.contains('^Unnamed')]
#         company_df = company_df.dropna(how='all')
#         company_df = company_df.sort_values(by='date',ascending=True).reset_index(drop=True)
#         match_index = company_df[company_df['date'].isin([df['date'][i]])].index
#         tomorrow = company_df.iloc[match_index+1]
#         df['내일날짜'][i] = tomorrow.iloc[0][1]
    
# 파일 추출
df.to_csv(PATH + "catch_highest/data/extracted_data/20201027_date_company_list.csv", encoding="utf-8-sig")