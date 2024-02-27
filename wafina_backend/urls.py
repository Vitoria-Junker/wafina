"""wafina_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Wafina APIs",
      default_version='v1',
      description="Wafina Endpoint Description",
      contact=openapi.Contact(email="arun.bhatt077@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

apis = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include("accounts.urls")),
    url(r'^api/v1/', include("notifications.urls")),
    url(r'^api/v1/', include("booking_requests.urls")),
    url(r'^api/v1/', include("user_feed.urls")),
    url(r'^api/v1/', include("funds.urls")),
    url(r'^api/v1/', include("reviews.urls")),
    url(r'^api/v1/', include("chat_app.urls")),
    url(r'^api/v1/', include("home.urls")),
]

urlpatterns = [
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger'),
 ] + apis
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)