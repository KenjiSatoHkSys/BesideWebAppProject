from django.urls import path
from . import views

app_name = 'BesideWebApp'
urlpatterns = [
    path('', views.viewslogin, name='viewslogin'),
    path('logout', views.viewslogout, name='viewslogout'),
    path('index', views.index, name='index'),  # (パラメータ)第1：アドレスバーのURL、第2：views.pyの中のクラス名、
]
