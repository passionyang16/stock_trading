import pandas as pd
import numpy as np
import ast
import os
from tqdm import tqdm

# 상따 목록 불러오기
df = pd.read_csv("date_company_list_kospi_entire.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

for i in range(df.shape[0]):
    df['상한가'][i] = ast.literal_eval(df['상한가'][i])
    # df['다음날수익률'][i] = ast.literal_eval(df['다음날수익률'][i])

df['내일날짜'] = [0 for x in range(len(df.index))]


for i in tqdm(range(df.shape[0] - 1)):
    try:
        for j in df['상한가'][i]:
            company_df = pd.read_csv("C:\\Users\\user\\Desktop\\kospi_list_600_entire(0914)\\%s.csv" % j)
            company_df = company_df.loc[:, ~company_df.columns.str.contains('^Unnamed')]
            company_df = company_df.dropna(how='all')
            company_df = company_df.sort_values(by='date', ascending=True).reset_index(drop=True)
            match_index = company_df[company_df['date'].isin([df['date'][i]])].index
            tomorrow = company_df.iloc[match_index + 1]
            df['내일날짜'][i] = tomorrow.iloc[0][0]
    except:
        continue
df = df[['내일날짜', '상한가']]
df.columns = ['상한가다음날', '상한가종목']

print(df)
dic={}
for i in range(len(df)):
    dic[df['상한가다음날'][i]]=df['상한가종목'][i]
print(dic)