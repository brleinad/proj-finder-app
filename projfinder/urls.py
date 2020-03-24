from django.urls import path

#from .views import ProjFinderView, projfinder_view
from .views import projfinder_view

urlpatterns = [
        #path('', ProjFinderView.as_view(), name='projfinder'),
        path('', projfinder_view, name='projfinder'),
        ]
