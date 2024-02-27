from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'notification/', apis.NotificationView.as_view(),
        name='notification'),
    url(r'bulk-notification-delete/', apis.NotificationBulkDelete.as_view(),
        name='bulk-notification-delete')
]