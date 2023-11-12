from django.http import JsonResponse
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

def get_relTopic(req):
    pytrends = TrendReq(hl='ko', tz=540)

    if req.method == 'GET':
        keyword = str(req.GET.get('keyword'))
        print("Getting keyword : ", keyword)
        keyword = keyword.replace(" ", "").lower()
        keywords = [keyword]

        #now = datetime.now()
        #presentDate = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
        #oneYearAgoDate = str(now.year - 1) + '-' + str(now.month) + '-' + str(now.day)
        #timeFrame = oneYearAgoDate + ' ' + presentDate

        pytrends.build_payload(keywords, cat=0, geo='KR')
        df_rt = pytrends.related_topics()
        df_rt['keyword'] = df_rt.pop(keyword)

        for key in df_rt:
            if isinstance(df_rt[key]['rising'], pd.DataFrame):
                df_rt[key]['rising'] = df_rt[key]['rising'].to_dict(orient='records')
            if isinstance(df_rt[key]['top'], pd.DataFrame):
                df_rt[key]['top'] = df_rt[key]['top'].to_dict(orient='records')

        def remove_keys(data, keys_to_remove):
            for main_key in data:
                for key in keys_to_remove:
                    if isinstance(data[main_key][key], list):
                        for item in data[main_key][key]:
                            item.pop('link', None)
                            item.pop('topic_mid', None)
                            item.pop('formattedValue', None)
                            item.pop('hasData', None)

            return data

        key_to_remove = ['rising','top']
        new_rt = remove_keys(df_rt, key_to_remove)
        print(new_rt)

        return JsonResponse(new_rt)
    else:
        return JsonResponse({'Error':'Bip! Error...'})
