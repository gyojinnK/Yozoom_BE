from django.http import JsonResponse
from pytrends.request import TrendReq
from datetime import datetime
from django.shortcuts import render
import urllib.request
import json
import pandas as pd
import plotly.express as px


def get_dl_trends(res):
    client_id = 'jtuR5ZJeQlYPlKMUJLwh'
    client_secret = 'JgrcAQiQqC'
    url = "https://openapi.naver.com/v1/datalab/search";

    now = datetime.now()
    end_date = str(now.year) + '-' + str(now.month) +  '-' + str(now.day)
    start_date = str(now.year - 5) + '-' + str(now.month) +  '-' + str(now.day)

    body = f'{{"startDate":"{start_date}","endDate":"{end_date}","timeUnit":"date","keywordGroups":[{{"groupName":"BTS","keywords":["BTS","english"]}}],"device":"pc","ages":["1","2"],"gender":"f"}}'

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    request.add_header("Content-Type","application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        response_data = response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

    result = json.loads(response_data)
    #print(result)

    date = [a['period'] for a in result['results'][0]['data']]
    ratio_data1 = [a['ratio'] for a in result['results'][0]['data']]

    dl_data = pd.DataFrame({'date':date,
                  'naver_datalab_d':ratio_data1})

    print(dl_data.head())

    #figure = px.line(dl_data, x="date", y="naver_datalab_d", title="결과")
    #figure.show()

    #dl_data_dict = dl_data.to_dict()
    return dl_data

def get_go_trends(req):
    pytrends = TrendReq(hl='ko', tz=540)
    #pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})

    kw_list = ["BTS"] #한번에 5개 키워드 제한

    #현재를 기준으로 1년동안으로 시간 설정
    now = datetime.now()
    end_date = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
    start_date = str(now.year-5) + '-' + str(now.month) + '-' + str(now.day)
    time_frame = start_date + ' ' + end_date

    pytrends.build_payload(kw_list, cat=0, timeframe=time_frame, geo='KR')
    go_data = pytrends.interest_over_time()
    go_data = go_data.reset_index()

    # date를 문자열로 변환: date 컬럼의 타입이 timestamp라 JSon형식으로 맞추기위해 진행
    go_data['date'] = go_data['date'].dt.strftime('%Y-%m-%d')

    go_data.rename(columns={'BTS':'pytrend_d'}, inplace=True)
    print(go_data.head())

    #go_dict = go_data.to_dict()

    return go_data

