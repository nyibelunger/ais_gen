from django.urls import path
from . import views

app_name = 'generator'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('input_excel/', views.input_excel, name='input_excel'),
    path('upload_date/', views.upload_date, name='upload_date'),
    path('input_date/', views.input_date, name='input_date'),
    path('render_sel_us_ais/', views.render_sel_us_ais, name='render_sel_us_ais'),
    path('home/', views.home, name='home'),
    #path('usr_input/usr_input_add/', views.usr_input_add, name='usr_input_add'),
               ]
