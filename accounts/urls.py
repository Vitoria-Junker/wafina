from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()
router.register('personal-information', apis.UserPersonalInfoAPI, basename='personal-info')
router.register('user-expertise', apis.SelectExpertiseAPI, basename='select-expertise')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^registration/$', apis.RegistrationAPI.as_view(), name='register'),
    url(r'^verify-otp/$', apis.VerifyOTPView.as_view(),
        name='verify-otp'),
    url(r'^login/$', apis.LoginView.as_view(), name='login'),
    url(r'^resend-otp/$', apis.ResendOtp.as_view(), name='resend'),
    url(r'^forgot-password/$', apis.ForgotPasswordAPIView.as_view(),
        name="forgot_password"),
    url(r'^reset-password/$', apis.OtpVerifyPasswordResetAPIView.as_view(),
        name="reset-password"),
    url(r'^expertise/$', apis.ExpertiseAPI.as_view(), name='expertise'),
    url(r'^search-users/$', apis.UserSearchAPI.as_view(), name='search'),
    url(r'^verify-my-account/$', apis.UserStripeVerification.as_view(), name='verification'),
    url(r'^skip-verification', apis.SkipVerification.as_view(), name='skip'),
    url(r'^change-password/$', apis.ChangePasswordView.as_view(), name="change-password"),
    url(r'^user-details/$', apis.UserDataAPI.as_view(), name="user-details"),
    url(r'^update-role/$', apis.UpdateRoleAPI.as_view(), name="role"),

]