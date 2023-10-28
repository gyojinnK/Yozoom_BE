from django.shortcuts import render
from django.http import JsonResponse
from pytrends.request import TrendReq
from datetime import datetime
import plotly.express as px

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

    # date를 문자열로 변환
    go_data['date'] = go_data['date'].dt.strftime('%Y-%m-%d')

    go_data.rename(columns={'BTS':'pytrend_d'}, inplace=True)
    print(go_data)

    go_dict = go_data.to_dict()

    return JsonResponse(go_dict)
