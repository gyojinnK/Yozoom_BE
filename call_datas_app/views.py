from django.http import JsonResponse
from pytrends.request import TrendReq
from datetime import datetime
from django.shortcuts import render
import urllib.request
import json
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta
from googletrans import Translator
from functools import reduce

def get_dl_trends(req):
    client_id = 'jtuR5ZJeQlYPlKMUJLwh'
    client_secret = 'JgrcAQiQqC'
    url = "https://openapi.naver.com/v1/datalab/search"
    translator = Translator()

    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - relativedelta(years=2)).strftime("%Y-%m-%d")


    def call_dl(keywords):
        df_list = []
        for word in keywords:
            ts_word = translator.translate(word, src='ko', dest='en')
            print('transedWord: ', ts_word.text)
            body_dict = {
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": "month",
                "keywordGroups": [
                    {
                        "groupName": word,
                        "keywords": [word, ts_word.text]
                    }
                ],
                "device": "pc",
                "ages": ["1", "2"],
                "gender": "f"
            }

            body = json.dumps(body_dict)

            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            request.add_header("Content-Type", "application/json")
            response = urllib.request.urlopen(request, data=body.encode("utf-8"))
            rescode = response.getcode()
            if (rescode == 200):
                response_body = response.read()
                response_data = response_body.decode('utf-8')
            else:
                print("Error Code:" + rescode)

            result = json.loads(response_data)

            date = [a['period'] for a in result['results'][0]['data']]
            ratio_data1 = [a['ratio'] for a in result['results'][0]['data']]

            dl_data = pd.DataFrame({'date': date, word: ratio_data1})
            dl_data[word] = dl_data[word].replace('nan', "")
            dl_data[word] = dl_data[word].fillna(method='ffill')

            df_list.append(dl_data)
            print('===== ', word, ' =====')
            print(dl_data.head())

        #concated_df = pd.concat(df_list, axis=1).groupby(level=0, axis=1).first()
        merged_df = reduce(lambda left, right: pd.merge(left, right, on='key_column'), df_list)
        print('===== merged DF =====')
        print(merged_df.head())

        return merged_df

    if req.method == 'GET':
        keyword = str(req.GET.get('keyword'))
        print(keyword)
        keyword = keyword.replace(" ", "").lower()
        keywords = []
        if keyword.find(','):
            keywords = keyword.split(sep=',')
            print('splited Keywords : ', keywords)
            dl_df = call_dl(keywords)
        else:
            keywords = [keyword]
            print('normal Keywords : ', keywords)
            dl_df = call_dl(keywords)

        dl_df_dict = dl_df.to_dict()
        print(dl_df_dict)
        return JsonResponse(dl_df_dict)
    else:
        return JsonResponse({'Error':'Bip! Error...'})

def get_go_trends(req):
    pytrends = TrendReq(hl='ko', tz=540)
    # pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})

    if req.method == 'GET':
        keyword = str(req.GET.get('keyword'))
        print("Getting keyword : ", keyword)
        keyword = keyword.replace(" ", "").lower()
        keywords = []
        if keyword.find(',') :
            keywords = keyword.split(sep=',')
            print('splited Keywords : ', keywords)
        else:
            keywords = [keyword]
            print('normal Keywords : ', keywords)


        #kw_list = ["BTS"]  # 한번에 5개 키워드 제한

        # 현재를 기준으로 1년동안으로 시간 설정
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - relativedelta(years=1)).strftime("%Y-%m-%d")
        time_frame = start_date + ' ' + end_date

        pytrends.build_payload(keywords, cat=0, timeframe=time_frame, geo='KR')
        go_data = pytrends.interest_over_time()
        go_data = go_data.reset_index()

        # date를 문자열로 변환: date 컬럼의 타입이 timestamp라 JSon형식으로 맞추기위해 진행
        go_data['date'] = go_data['date'].dt.strftime('%Y-%m-%d')

        print(go_data.head())

        go_data_dict = go_data.to_dict()

        print(go_data_dict)

        return JsonResponse(go_data_dict)
    else:
        return JsonResponse({'Error':'Bip! Error...'})

