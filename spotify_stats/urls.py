from django.urls import path

from . import views

app_name = 'spotify_stats'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:stream_id>/', views.detail, name='detail')
]
