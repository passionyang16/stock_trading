# Stock Trading

주식 자동 트레이딩 프로그램

## 가이드

- 해당 프로그램은 대신증권 크레온 HTS의 API를 사용하기에, Window OS에서만 가능 (Mac OS 불가)

- 가상환경을 활성화 시킨 후 `pip -r requirements.txt`를 실행시켜 필요한 패키지들을 설치

- 자동 트레이딩 관련 모든 .py 파일은 HTS에 미리 로그인이 되어 있어야 실행 가능

- 종목코드를 위주로 프로그램 매매가 진행

## 개요

[Version 1) 테마주 미리 사기](theme_stock/)

NLP를 활용하여 테마주를 미리 사서 정해진 밴드에 맞춰 매매

  - 네이버 뉴스에 테마, 뉴스, 종목 크롤링

  - KoBert로 Tokenize, Word2Vec으로 Vectorize

  - Stopwords와 정규표현식으로 meaningless한 데이터 전처리

  - 뉴스 vector와 테마 vector를 비교해 코사인 유사도가 가장 높은 테마 선정

  - 리스크를 줄이기 위해 +5% 상한선, -5% 하한선의 밴드를 설정하고, 해당 밴드를 벗어나면 매도

[Version 2) 상한가 따라잡기](catch_highest/)

변동성이 큰 상한가 다음날 종목을 매매

  - 대신증권 크레온 API로 2년치 상한가 다음날 종목 데이터 매분마다 수집

  - 몇시 몇분 매수, 몇시 몇분 매도가 가장 큰 수익률을 가져다주는지 정밀한 데이터 분석 진행

  - 대신증권 크레온 API request / response를 통해 주식 자동 트레이딩 프로그램 완성
