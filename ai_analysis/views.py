from call_datas_app.views import get_dl_trends
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from django.http import JsonResponse
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
from googletrans import Translator
import json
import urllib.request

N_STEPS = 3
N_FEATURES = 1

def prepare_data(mg):
    X, y = [], []
    for i in range(N_STEPS, len(mg)):
        X.append(mg[i-N_STEPS:i])
        y.append(mg[i])
    X, y = np.array(X), np.array(y)
    return X, y

def predict_values(model, X_input, n_steps=10):
    y_preds = []
    for _ in range(n_steps):
        X_input = X_input.reshape((1, N_STEPS, N_FEATURES))
        y_pred = model.predict(X_input)
        y_preds.append(y_pred[0][0])
        X_input = np.append(X_input[0][1:], y_pred)
    return y_preds

def analysis_view(req):
    client_id = 'jtuR5ZJeQlYPlKMUJLwh'
    client_secret = 'JgrcAQiQqC'
    url = "https://openapi.naver.com/v1/datalab/search"

    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - relativedelta(years=2)).strftime("%Y-%m-%d")
    translator = Translator()

    if req.method == 'GET':
        keyword = str(req.GET.get('keyword'))
        print("Getting keyword : ", keyword)
        keyword = keyword.replace(" ", "").lower()
        ts_word = translator.translate(keyword, src='ko', dest='en')
        body_dict = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "month",
            "keywordGroups": [
                {
                    "groupName": keyword,
                    "keywords": [keyword, ts_word.text]
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

        dl_datas = pd.DataFrame({'date': date, keyword: ratio_data1})
        dl_datas[keyword] = dl_datas[keyword].replace('nan', "")
        dl_datas[keyword] = dl_datas[keyword].fillna(method='ffill')

    # dl_datas_json = get_dl_trends(req)
    # dl_json = dl_datas_json.content.decode('utf-8')
    # dl_datas = pd.read_json(dl_json)
        dl_datas.columns = ['date', 'keyword']

        print('dl_datas df: ', dl_datas)

        # 데이터 스케일링
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dl_datas['keyword'].values.reshape(-1,1))

        # 데이터 준비
        X, y = prepare_data(scaled_data)

        # 학습된 모델 불러오기
        model = load_model('./model/my_model.h5')

        # 예측 데이터
        X_input = X[-1]
        y_pred = predict_values(model, X_input)

        # 예측 결과를 원래의 범위로 역변환
        y_pred_inv = scaler.inverse_transform(np.array(y_pred).reshape(-1, 1))

        # 예측 결과가 0~100 범위를 벗어나지 않도록 제한
        y_pred_inv = np.clip(y_pred_inv, 0, 100)

        pred_result = {"Predicted Value": y_pred_inv.flatten().tolist()}

        return JsonResponse(pred_result)
