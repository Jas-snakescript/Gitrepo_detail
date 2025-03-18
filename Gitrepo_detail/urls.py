from django.urls import path
from . import views

app_name = 'gitrepo'

urlpatterns = [
    path('', views.home, name='home'),
    path('user-detail/', views.user_detail, name='user_detail'),
]