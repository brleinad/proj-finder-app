from django.urls import path

from .views import ProjFinderView, proj_finder_view

urlpatterns = [
        #path('', ProjFinderView.as_view(), name='projfinder'),
        path('', proj_finder_view, name='projfinder'),
        ]
