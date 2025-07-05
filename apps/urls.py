from django.urls import path,include
from .views import my_view,fun,login,dashboard,create_scrape,get_scraped_data,get_ksa
urlpatterns = [
    path('hello/', my_view, name='home'),
    path('scrape/',fun, name='scrape'),
    path('',login,name="login"),
    path('dashboard/',dashboard,name="dashboard"),
    path('create-scrape/',create_scrape,name="create_scrape"),
    path('get_scraped_data/',get_scraped_data, name="get_scraped_data"),
    # path('get_scraped_data/<str:make>/<str:model>/<str:website>/<str:uuid>/<str:country>/<str:city>/',get_scraped_data, name="get_scraped_data"),
    path('ksa/',get_ksa,name="get_ksa")
]