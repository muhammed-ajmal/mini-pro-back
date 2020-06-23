from django.conf.urls import url
from .views import CreateUserAPIView, LogoutUserAPIView,account_batch, account_department,CreateAccountBatchAPIView,obtain_auth_token
from .views import ActivateAccount,ResetAccountPassword, ManuelVerificationAPIView

urlpatterns = [
    url(r'^auth/login/$',
        obtain_auth_token,
        name='auth_user_login'),
    url(r'^auth/register/$',
        CreateUserAPIView.as_view(),
        name='auth_user_create'),
    url(r'^auth/logout/$',
        LogoutUserAPIView.as_view(),
        name='auth_user_logout'),
    url(r'^auth/account/reset$', ActivateAccount.as_view()),
    url(r'^auth/account/password/reset$', ResetAccountPassword.as_view()),
    url(r'^auth/account/create/batches/$',CreateAccountBatchAPIView.as_view()),
    url(r'^auth/account/get/batches/$', account_batch),
    url(r'^auth/account/get/departments/$', account_department),
    url(r'^auth/account/verify/alumni/manuel/$', ManuelVerificationAPIView.as_view())

]
