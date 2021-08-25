from django.urls import path

from . import views
from .views import BasicStats

app_name = 'spotify_stats'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:stream_id>/', views.detail, name='detail'),
    path('basic_stats/<int:track_id>/', BasicStats.as_view(), name='basic_stats'),
    path('pick_date/', views.pick_date, name='pick_date'),
    path('most_listened/', views.most_listened, name='most_listened'),
]
