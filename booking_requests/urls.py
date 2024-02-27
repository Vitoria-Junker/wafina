from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'send-booking-request/', apis.SendProposalView.as_view(),
        name='booking-request'),
    url(r'session-details/$', apis.SessionDetailsAPI.as_view(),
        name='session-details'),
    url(r'session-action/$', apis.SessionActionAPI.as_view(),
        name='session-action'),
    url(r'calender-data/$', apis.CalenderDataView.as_view(),
        name='calender'),
]