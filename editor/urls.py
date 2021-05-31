from django.urls import path

from . import views

appname = 'editor'

urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update_view, name='update'),
    path('download/<int:pk>/', views.download, name='download'),
]
