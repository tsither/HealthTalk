from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('page1/', views.page1_view, name='page1'),
    path('page2/', views.page2_view, name='page2'),
    path('page3/', views.page3_view, name='page3'),
    path('page3_3/', views.page3_3, name='page3_3'),
]
