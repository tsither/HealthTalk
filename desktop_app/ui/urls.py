from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('page1/', views.page1_view, name='page1'),
    path('page2/', views.page2_view, name='page2'),
    path('page3/', views.page3_view, name='page3'),
    # path('chatbot/', views.chatbot_view, name='chatbot'),
    path('page2/process', views.process_reports, name='process_reports'),
    path('page2/success', views.upload_success, name='upload_success'),
]