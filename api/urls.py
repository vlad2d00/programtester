from django.urls import path, include, re_path
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'tests', viewset=TestViewSet, basename=Test.__name__.lower())
router.register(r'results', viewset=TestRequestViewSet, basename=TestRequest.__name__.lower())

urlpatterns = [
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    path('', include(router.urls)),

]
