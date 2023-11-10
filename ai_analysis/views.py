from django.shortcuts import render
from call_datas_app.views import get_go_trends
from call_datas_app.views import get_dl_trends
from django.http import JsonResponse
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense, Dropout, LSTM
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf
import pandas as pd
import numpy as np

N_STEPS = 3
N_FEATURES = 1

def prepare_data(mg):
    X, y = [], []
    for i in range(N_STEPS, len(mg)):
        X.append(mg['weigth_search_volume'][i-N_STEPS:i].values)
        y.append(mg['weigth_search_volume'][i])
    X, y = np.array(X), np.array(y)
    return X, y

def train_model(X, y):
    # Early stopping callback 설정
    early_stopping = EarlyStopping(monitor='val_loss',
                                 patience=10,
                                 restore_best_weights=True)

    kfold = KFold(n_splits=5)

    mae_scores = []
    rmse_scores = []

    for train_index, val_index in kfold.split(X):
        X_train_kf, X_val_kf = X[train_index], X[val_index]
        y_train_kf, y_val_kf = y[train_index], y[val_index]

        # 모델 구성 및 컴파일
        model = Sequential()
        model.add(LSTM(50,
                       activation='relu',
                       input_shape=(N_STEPS, N_FEATURES)))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')

        # 학습 데이터 차원 변경 (샘플 수 x 시퀀스 길이 x 피처 수)
        X_train_kf = X_train_kf.reshape((X_train_kf.shape[0], X_train_kf.shape[1], N_FEATURES))
        X_val_kf = X_val_kf.reshape((X_val_kf.shape[0], X_val_kf.shape[1], N_FEATURES))

        # 모델 학습 및 검증
        history = model.fit(X_train_kf,
                          y_train_kf,
                          validation_data=(X_val_kf, y_val_kf),
                          epochs=200,
                          batch_size=16,
                          callbacks=[early_stopping])

        # 검증 데이터에 대한 예측 수행
        y_pred = model.predict(X_val_kf)

        # MAE 계산
        mae = mean_absolute_error(y_pred, y_val_kf)
        mae_scores.append(mae)

        # RMSE 계산
        rmse = np.sqrt(mean_squared_error(y_pred, y_val_kf))
        rmse_scores.append(rmse)

    print("Average MAE score : ", np.mean(mae_scores))
    print("Average RMSE score : ", np.mean(rmse_scores))

    # 학습된 모델 반환
    return model

def predict_values(model, X_input):
    X_input = X_input.reshape((1, X_input.shape[0], N_FEATURES))  # 입력 차원 변경
    y_pred = model.predict(X_input)  # 예측 수행
    return y_pred[0][0]  # 예측값 반환


def analysis_view(res):
    go_datas_json = get_go_trends(res)
    dl_datas_json = get_dl_trends(res)
    go_datas = pd.read_json(go_datas_json)
    dl_datas = pd.read_json(dl_datas_json)

    mg = pd.merge(go_datas, dl_datas, on='date')
    mg.drop('isPartial', axis=1, inplace=True)
    mg['pytrend_d'].fillna(mg['pytrend_d'].mean(), inplace=True)
    # mg.to_csv('mg_test.csv')

    # 임의의 가중치 설정
    pt_weight = 0.3
    nd_weight = 0.7

    mg['weigth_search_volume'] = pt_weight * mg['pytrend_d'] + nd_weight * mg['naver_datalab_d']

    min_v = mg['weigth_search_volume'].min()
    max_v = mg['weigth_search_volume'].max()
    mg['weigth_search_volume'] = (mg['weigth_search_volume'] - min_v) / (max_v - min_v) * 1

    print(mg.weigth_search_volume)

    # 데이터 전처리
    X, y = prepare_data(mg)
    # AI 모델 학습
    model = train_model(X, y)

    # 에측 데이터
    X_input = np.array(mg['weigth_search_volume'][-N_STEPS:])
    y_pred = str(predict_values(model, X_input))

    pred_result = {"Predicted Value": y_pred}

    return JsonResponse(pred_result)

