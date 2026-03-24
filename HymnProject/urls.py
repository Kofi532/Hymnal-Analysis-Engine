from django.urls import path
from analytics import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('data/', views.raw_data_table, name='raw_data'),
    path('data/source/', views.raw_json_table, name='raw_source'),
]



