from django.urls import path

from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.index, name='index'),
    path('data/scrape', views.scrape_tweets, name='scrape'),
    path('data/classify', views.classify_tweets, name='classify')
]
