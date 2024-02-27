from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'conversations/', apis.ConversationAPI.as_view(),
        name='conversation'),
    url(r'unseen-messages/$', apis.UnseenMessageCount.as_view(),
        name='unseen'),
    url(r'chat-dashboard/$', apis.InteractionsAPI.as_view(),
        name='dashboard'),
    url(r'all-new-messages/$', apis.UnseenConversations.as_view(),
        name='new_messages')
]