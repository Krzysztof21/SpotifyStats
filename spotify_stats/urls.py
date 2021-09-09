from django.urls import path

from . import views
from .views import BasicStats

app_name = 'spotify_stats'
urlpatterns = [
    path('', views.index, name='index'),
    path('streams/<int:pk>/', views.StreamDetailView.as_view(), name='stream_detail'),
    path('tracks/<int:pk>/', views.TrackDetailView.as_view(), name='track_detail'),
    path('basic_stats/<int:track_id>/', BasicStats.as_view(), name='basic_stats'),
    path('pick_date/', views.PickDateFormView.as_view(), name='pick_date'),
    path('most_listened/', views.MostListenedListView.as_view(), name='most_listened'),
    path('pie_chart/', views.pie_chart, name='pie-chart'),
]
