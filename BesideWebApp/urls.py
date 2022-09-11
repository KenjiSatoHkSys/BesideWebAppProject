from django.urls import path
from . import views

app_name = 'BesideWebApp'

# Herokuでは24h周期でアプリ(dyno)の再起動が行われる。
# ログイン処理を持たせている場合、再起動後のリクエストに対しては Not found が画面に表示され停止してしまう。
# よって、ログイン処理はなしにする必要あり。

urlpatterns = [
#   path('', views.viewslogin, name='viewslogin'),
#   path('logout', views.viewslogout, name='viewslogout'),
    path('', views.index, name='index0'),
    path('index', views.index, name='index1'),
]
