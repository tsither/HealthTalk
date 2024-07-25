from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('page1/', views.page1_view, name='page1'),
    path('page2_1/', views.page2_1view, name='page2_1'),
    path('page2/process', views.process_reports, name='process_reports'),
    path('page2/success', views.upload_success, name='upload_success'),
    path('page2_2/', views.page2_2view, name='page2_2'),
    path('page3/', views.page3_view, name='page3'),
    path('page3_3/', views.page3_3, name='page3_3'),
    # path('chatbot/', views.chatbot_view, name='chatbot'),
    path('convert_to_sql/', views.convert_to_sql, name='convert_to_sql'),
   
]
