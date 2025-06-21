from django.urls import path,include
from .views import my_view,fun,login,dashboard,create_scrape,get_scraped_data
urlpatterns = [
    path('hello/', my_view, name='home'),
    path('scrape/',fun, name='scrape'),
    path('login/',login,name="login"),
    path('dashboard/',dashboard,name="dashboard"),
    path('create-scrape/',create_scrape,name="create_scrape"),
    path('get_scraped_data/<str:make>/<str:model>/',get_scraped_data, name="get_scraped_data"),
]