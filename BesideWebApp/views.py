from django.contrib.sites import requests
from django.http import request
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import requests
import datetime
import time
from .models import Beside_db
from .models import Openweather_db
from .models import Manager_db


class beside:
    def __init__(self, url, no, disp_name, co2_cal, map_x, map_y):
        self.url = url
        self.no = no
        self.disp_name = disp_name
        self.co2_cal = co2_cal
        self.map_x = map_x
        self.map_y = map_y

    def current(self):  # 現在値取得（Beside）
        data = getapidata(self.url, {})  # Beside data
#        data = ''  # dummy data for development

        # 正常にデータが取得できた場合の処理（keyとして下記の文字列が含まれたjsonファイルが取得される）
        if ('CO' in data) and ('TP_refined' in data) and ('HM_refined' in data):
            co2 = data['CO'] + self.co2_cal
            t = data['TP_refined']
            h = data['HM_refined']
            thi = 0.81*t+0.01*h*(0.99*t-14.3)+46.3  # 不快指数＝0.81×気温＋0.01×湿度（0.99×気温－14.3）＋46.3
            thi_st = thi_stats(thi)
            t_str = '{:.1f}'.format(t)
            h_str = '{:.1f}'.format(h)
            thi_str = '{:.1f}'.format(thi)
            time_str = data['created_on']  # 生データ書式→　　2022-08-24T11:01:53Z
            time_str = time_str.replace('T', ' ').replace('Z', '')
            time_val = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            time_val = time_val + datetime.timedelta(hours=9)
            time_str = time_val.strftime('%Y-%m-%d %H:%M')
            return {
                'no': self.no,
                'disp_name': self.disp_name,
                'map_x': self.map_x,
                'map_y': self.map_y,
                'temp': t_str,
                'humid': h_str,
                'thi': thi_str,
                'thi_css_class': thi_st['css_class'],
                'thi_nickname': thi_st['nickname'],
                'co2': co2,
                'mtime': time_str
            }
        else:  # 正常にデータが取得できなかった場合は表には'-'を記載
            return {
                'no': self.no,
                'disp_name': self.disp_name,
                'map_x': self.map_x,
                'map_y': self.map_y,
                'temp': '-',
                'humid': '-',
                'thi': '-',
                'thi_css_class': 'thtable_lv0',
                'thi_nickname': '-',
                'co2': '-',
                'mtime': '-'
            }


class OpenWeather:
    def __init__(self, url_init, url, api_key, user_loc):  # API keyおよびデータ取得地域名を送信し、同地域の緯度・軽度を取得
        self.user_loc_lon = -99  # 経度の初期値。データが取得できない場合はこのままの値となりサーバーダウンの目印とする
        self.user_loc_lat = -99  # 軽度の初期値。データが取得できない場合はこのままの値となりサーバーダウンの目印とする
        self.api_key = api_key
        self.url = url  # データ取得用url
        data = getapidata(  # ユーザーの居住地域の位置情報を取得
                url_init,
            {
                "appid": self.api_key,
                "q": user_loc,  # ex. OSAKA
                "lang": "ja"
            }
        )
        # keyとして'coord', 'lon', 'lat'を含んだjsonファイルであれば正常にデータ取得できたものとして格納
        if 'coord' in data:
            self.user_loc_lon = data["coord"]["lon"]  # 経度
            self.user_loc_lat = data["coord"]["lat"]  # 緯度

    def current(self):  # 現在値取得（外気データ）
#        opwdata = ''  # dummy data for development
        opwdata = getapidata(  # 気象データ取得
            self.url,  # "https://api.openweathermap.org/data/2.5/onecall",
            {
                "appid": self.api_key,
                "lon": self.user_loc_lon,
                "lat": self.user_loc_lat,
                "units": "metric",
                "lang": "ja",
                "exculde": "current,minutely,hourly,alerts"
            }
        )
        if 'current' in opwdata:  # 正常にデータが取得できた場合の処理（keyとして'current'の文字列が含まれたjsonファイルが取得される）
            t = opwdata["current"]["temp"]
            h = opwdata["current"]["humidity"]
            thi = 0.81*t+0.01*h*(0.99*t-14.3)+46.3  # 不快指数＝0.81×気温＋0.01×湿度（0.99×気温－14.3）＋46.3
            thi_st = thi_stats(thi)
            t_str = '{:.1f}'.format(t)
            h_str = '{:.1f}'.format(h)
            thi_str = '{:.1f}'.format(thi)
            time_val = opwdata["current"]["dt"]  # unix time（ex. 1661660069)
            time_val = datetime.datetime.fromtimestamp(time_val)  # 2022-08-28 13:14:29
#            time_val = time_val + datetime.timedelta(hours=-9)
            time_str = time_val.strftime('%Y-%m-%d %H:%M')
            return {
                'no': '外',
                'disp_name': '外気',
                'map_x': 1.1,
                'map_y': 1.1,
                'temp': t_str,
                'humid': h_str,
                'thi': thi_str,
                'thi_css_class': thi_st['css_class'],
                'thi_nickname': thi_st['nickname'],
                'co2': '-',
                'mtime': time_str
            }
        else:  # 正常にデータが取得できなかった場合は表には'-'を記載
            return {
                'no': '外',
                'disp_name': '外気',
                'map_x': 1.1,
                'map_y': 1.1,
                'temp': '-',
                'humid': '-',
                'thi': '-',
                'thi_css_class': 'thtable_lv0',
                'thi_nickname': '-',
                'co2': '-',
                'mtime': '-'
            }


def getapidata(endpoint, params):
    try:  # 正常に結果が得られた場合の処理
        result = requests.get(endpoint, params)
        return result.json()
    except requests.exceptions.RequestException as e:  # 結果が得られなかった場合の処理
        return 'noresult'


def thi_stats(THI):  # 不快指数の色を返す
    if 85 <= THI:
        return {'css_class': 'thtable_lv9', 'nickname': '暑3'}  # 暑くてたまらない
    elif 80 <= THI < 85:
        return {'css_class': 'thtable_lv8', 'nickname': '暑2'}  # 暑くて汗が出る
    elif 75 <= THI < 80:
        return {'css_class': 'thtable_lv7', 'nickname': '暑1'}  # やや暑い
    elif 70 <= THI < 75:
        return {'css_class': 'thtable_lv6', 'nickname': '許容'}  # 暑くない
    elif 65 <= THI < 70:
        return {'css_class': 'thtable_lv5', 'nickname': '快適'}  # 快適
    elif 60 <= THI < 65:
        return {'css_class': 'thtable_lv4', 'nickname': '快適'}  # 何も感じない
    elif 55 <= THI < 60:
        return {'css_class': 'thtable_lv3', 'nickname': '寒1'}  # 肌寒い
    elif 50 <= THI < 55:
        return {'css_class': 'thtable_lv2', 'nickname': '寒2'}  # 寒い
    elif THI < 50:
        return {'css_class': 'thtable_lv1', 'nickname': '寒3'}  # 寒くてたまらない


def index22(request):
    # Beside使用準備
    besides = []  # 全Besideのコレクション
    props = Beside_db.objects.all().values()
#    props = [
#        {'no': 1, 'room_name': 'kikaku_05_2516', 'co2_cal': 128, 'map_x': 0.6, 'map_y': 0.25, 'disp_name': '知財G'},
#        {'no': 2, 'room_name': 'kikaku_08_2452', 'co2_cal': 17, 'map_x': 0.94, 'map_y': 0.3, 'disp_name': '打合せコーナーC'},
#        {'no': 3, 'room_name': 'kikaku_02_2450', 'co2_cal': 197, 'map_x': 0.5, 'map_y': 0.4, 'disp_name': '原価企画_財務G（モニタ横）'},
#        {'no': 4, 'room_name': 'kikaku_10_2451', 'co2_cal': 28, 'map_x': 0.097, 'map_y': 0.7, 'disp_name': 'フリロケエリア（管理G側）'},
#        {'no': 5, 'room_name': 'kikaku_01_2519', 'co2_cal': 115, 'map_x': 0.25, 'map_y': 0.7, 'disp_name': 'フリロケエリア（経企G側）'},
#        {'no': 6, 'room_name': 'kikaku_03_2520', 'co2_cal': -83, 'map_x': 0.42, 'map_y': 0.7, 'disp_name': '原価企画_財務G（管理G側）'},
#        {'no': 7, 'room_name': 'kikaku_09_2454', 'co2_cal': 0, 'map_x': 0.57, 'map_y': 0.7, 'disp_name': '原価企画_財務G（打A側）'},
#        {'no': 8, 'room_name': 'kikaku_06_2455', 'co2_cal': -42, 'map_x': 0.77, 'map_y': 0.7, 'disp_name': '法規G_国際標準化G'},
#        {'no': 9, 'room_name': 'kikaku_07_2457', 'co2_cal': -232, 'map_x': 0.94, 'map_y': 0.63, 'disp_name': '打合せコーナーA'}
#        ]

    for prop in props:  # besideインスタンス作成
        besideAPIURL = 'https://e23hecpmok.execute-api.ap-northeast-1.amazonaws.com/dev/get_besidedata_for_test?room_name='  # API url
        besideAPIURL = besideAPIURL + prop['room_name']
        x = '{:.0f}'.format(prop['map_x'] * 350)
        y = '{:.0f}'.format(prop['map_y'] * 350)
        bsd = beside(url=besideAPIURL, no=prop['no'], co2_cal=prop['co2_calib'], disp_name=prop['disp_name'],
                     map_x=x, map_y=y)
        besides.append(bsd)  # 各besideをコレクションへ追加

    # OpenWeather使用準備
    props_o = Openweather_db.objects.all().values()
    opw = OpenWeather(url_init=props_o[0]['url_init'], url=props_o[0]['url_meas'],
                      api_key=props_o[0]['api_key'], user_loc=props_o[0]['location'])

    # 現在値の取得
    data = []  # 表示データのコレクション
    for bsd in besides:        # 現在値の取得(beside)
        data.append(bsd.current())  # 現在値の取得(beside)→コレクションへ追加
    data.append(opw.current())      # 現在値の取得(Open weather)→コレクションへ追加

    # データ更新周期
    props_m = Manager_db.objects.all().values()

    params = {
        'cycle': props_m[0]['cycle'],  # データ更新周期
        'data': data,
    }
    return render(request, 'BesideWebApp/index.html', params)
