from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()
router.register('reviews', apis.ReviewAPI, basename='reviews')


urlpatterns = [
    url(r'^', include(router.urls)),
]