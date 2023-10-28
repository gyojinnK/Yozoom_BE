from django.shortcuts import render
from pytrendapp.views import get_go_trends as go_data
from datalabapp.views import get_dl_trends as dl_data
import pandas as pd

# Create your views here.
def analysis_view(res):
    pt = pd.read_csv('pytrends_data.csv')
    nd = pd.read_csv('naver_datalab_data.csv')

    mg = pd.merge(pt, nd, on='date')
    mg.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'isPartial'], axis=1, inplace=True)
    mg['pytrend_d'].fillna(mg['pytrend_d'].mean(), inplace=True)
    # mg.to_csv('mg_test.csv')

    pt_weight = 0.3
    nd_weight = 0.7

    mg['weigth_search_volume'] = pt_weight * mg['pytrend_d'] + nd_weight * mg['naver_datalab_d']

    min_v = mg['weigth_search_volume'].min()
    max_v = mg['weigth_search_volume'].max()
    mg['weigth_search_volume'] = (mg['weigth_search_volume'] - min_v) / (max_v - min_v) * 1

    # mg.to_csv('calc_mg_test.csv')
    print(mg.weigth_search_volume)