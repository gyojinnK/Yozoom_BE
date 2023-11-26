from call_datas_app.views import get_dl_trends
from tensorflow.keras.models import load_model
from django.http import JsonResponse
import pandas as pd
import numpy as np

N_STEPS = 3
N_FEATURES = 1

def prepare_data(mg):
    X, y = [], []
    for i in range(N_STEPS, len(mg)):
        X.append(mg['keyword'][i-N_STEPS:i].values)
        y.append(mg['keyword'][i])
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

def analysis_view(res):
    dl_datas_json = get_dl_trends(res)
    dl_json = dl_datas_json.content.decode('utf-8')
    dl_datas = pd.read_json(dl_json)
    dl_datas.columns = ['date', 'keyword']

    print('dl_datas df: ', dl_datas)

    # 학습된 모델 불러오기
    model = load_model('./model/my_model.h5')

    # 예측 데이터
    X_input = np.array(dl_datas['keyword'][-N_STEPS:])
    y_pred = str(predict_values(model, X_input))

    pred_result = {"Predicted Value": y_pred}

    return JsonResponse(pred_result)
