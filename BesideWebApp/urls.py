from django.urls import path
from . import views

app_name = 'BesideWebApp'

urlpatterns = [
    path('', views.viewslogin, name='viewslogin'),
#   path('logout', views.viewslogout, name='viewslogout'),
#   path('', views.index, name='index0'),
    path('index', views.index, name='index1'),
]
