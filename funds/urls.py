from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'make-payments/', apis.TransactionAPI.as_view(),
        name='payments'),
    url(r'wallet/', apis.WalletAPI.as_view(),
        name='wallet'),
]