from django.urls import path
from . import views

app_name = 'BesideWebApp'
urlpatterns = [
    path('', views.index22, name='index33'),  # (パラメータ)第1：アドレスバーのURL、第2：views.pyの中のクラス名、
]
