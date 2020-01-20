from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fields', views.fields, name='fields'),
    path('locations', views.locations, name='locations'),
    # path('objects/<id>', views.objects, name='objects'),
    path('info/<id>', views.info, name='info'),
]
