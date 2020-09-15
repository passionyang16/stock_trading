from konlpy.tag import Mecab
import pandas as pd
mecab = Mecab()

#데이터 불러오기
politics_data = pd.read_csv('정치_202005.csv')
politics_data.columns = ['news']
science_data = pd.read_csv('IT과학_202005.csv')
science_data.columns = ['news']
economics_data = pd.read_csv('경제_202005.csv')
economics_data.columns = ['news']
culture_data = pd.read_csv('생활문화_202005.csv')
culture_data.columns = ['news']
society_data = pd.read_csv('사회_202005.csv')
society_data.columns = ['news']
world_data = pd.read_csv('세계_202005.csv')
world_data.columns = ['news']

#중복값 처리
politics_data = politics_data.drop_duplicates(['news'], keep='first')
science_data = science_data.drop_duplicates(['news'], keep='first')
economics_data = economics_data.drop_duplicates(['news'], keep='first')
culture_data = culture_data.drop_duplicates(['news'], keep='first')
society_data = society_data.drop_duplicates(['news'], keep='first')
world_data = world_data.drop_duplicates(['news'], keep='first')

# 모든 행을 하나로 합치기
politics_one = []
science_one = []
economics_one = []
culture_one = []
society_one = []
world_one = []

for i in politics_data['news']:
    politics_one.append(i)

for j in science_data['news']:
    science_one.append(j)

for k in economics_data['news']:
    economics_one.append(k)

for l in culture_data['news']:
    culture_one.append(l)

for m in society_data['news']:
    society_one.append(m)

for n in world_data['news']:
    world_one.append(n)


#명사로 자연어 처리하기
politics_mecab = mecab.nouns(str(politics_one))
science_mecab = mecab.nouns(str(science_one))
economics_mecab = mecab.nouns(str(economics_one))
culture_mecab = mecab.nouns(str(culture_one))
society_mecab = mecab.nouns(str(society_one))
world_mecab = mecab.nouns(str(world_one))

# 길이가 한개 짜리는 지우기
for a in range(len(politics_mecab) - 1, 0, -1):
    if len(politics_mecab[a]) == 1:
        politics_mecab.remove(politics_mecab[a])

for b in range(len(science_mecab) - 1, 0, -1):
    if len(science_mecab[b]) == 1:
        science_mecab.remove(science_mecab[b])

for c in range(len(economics_mecab) - 1, 0, -1):
    if len(economics_mecab[c]) == 1:
        economics_mecab.remove(economics_mecab[c])

for d in range(len(culture_mecab) - 1, 0, -1):
    if len(culture_mecab[d]) == 1:
        culture_mecab.remove(culture_mecab[d])

for e in range(len(society_mecab) - 1, 0, -1):
    if len(society_mecab[e]) == 1:
        society_mecab.remove(society_mecab[e])

for f in range(len(world_mecab) - 1, 0, -1):
    if len(world_mecab[f]) == 1:
        world_mecab.remove(world_mecab[f])

#나누어진 명사 개수 세기
from collections import Counter
politics_counted = dict(Counter(politics_mecab))
science_counted = dict(Counter(science_mecab))
economics_counted = dict(Counter(economics_mecab))
culture_counted = dict(Counter(culture_mecab))
society_counted = dict(Counter(society_mecab))
world_counted = dict(Counter(world_mecab))

# 해당 딕셔너리의 key,value값을 따로 분리하기

politics = []
politics_num = []
for key1, value1 in politics_counted.items():
    politics.append(key1)
    politics_num.append(value1)

science = []
science_num = []
for key2, value2 in science_counted.items():
    science.append(key2)
    science_num.append(value2)

economics = []
economics_num = []
for key3, value3 in economics_counted.items():
    economics.append(key3)
    economics_num.append(value3)

culture = []
culture_num = []
for key4, value4 in culture_counted.items():
    culture.append(key4)
    culture_num.append(value4)

society = []
society_num = []
for key5, value5 in society_counted.items():
    society.append(key5)
    society_num.append(value5)

world = []
world_num = []
for key6, value6 in world_counted.items():
    world.append(key6)
    world_num.append(value6)


#하나로 합치기
politics_df = {'politics':politics, 'politics_num':politics_num}
science_df = {'science':science, 'science_num':science_num}
economics_df = {'economics':economics, 'economics_num':economics_num}
culture_df = {'culture':culture, 'culture_num':culture_num}
society_df = {'society':society, 'society_num':society_num}
world_df = {'world':world, 'world_num':world_num}

politics_df = pd.DataFrame(politics_df)
science_df = pd.DataFrame(science_df)
economics_df = pd.DataFrame(economics_df)
culture_df = pd.DataFrame(culture_df)
society_df = pd.DataFrame(society_df)
world_df = pd.DataFrame(world_df)

final = pd.concat([politics_df,science_df,economics_df,culture_df,society_df,world_df],axis=1)

final.to_csv('keyword_sorting.csv', sep=',', encoding='utf-8-sig')