from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'contact-us/', apis.ContactUsAPI.as_view(),
        name='contact'),
    url(r'faq/', apis.FaqAPI.as_view(),
        name='faq')
]