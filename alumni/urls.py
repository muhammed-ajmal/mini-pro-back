"""alumni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from django.contrib.auth import views as auth_views
from account.views import alumni
from home import views as home_views

from community import views as community_views
from fundraiser import views as fund_views


urlpatterns = [
    path('admin/', admin.site.urls,),
    path('api/', include('api.urls')),
    path('signup/', alumni.AlumniSignUpView.as_view(), name='signup'),
    path('signup/add/batch',alumni.AddBatchView.as_view(), name = 'add_batch'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/update/password', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='change_password'),
    path('profile/update/password/done', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt',
            from_email='noreply@mg.alumni-cucek.ml'
        ),
        name='password_reset'),
    path('reset/done',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    path('reset/complete',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('profile/update/email', alumni.update_email, name = 'update_email'),
    path('profile/update/phone', alumni.send_sms, name = 'send_sms'),
    path('verification/token/', alumni.sms_token_validation, name='sms_token_validation'),  # noqa: E501
    path('profile/update/account', alumni.update_profile, name='update_profile'),
    path('fundraiser/',fund_views.home,name='fundraiser'),
    path('contribute/response/', fund_views.response),
    path('contribute/pay/<eventid>/',fund_views.Amount, name='contribute_event'),
    path('contribute/<eventid>/<orderid>/<amount>/',fund_views.payment,name='payment'),
    path('connect/sso', community_views.sso),
    path('connect/batchs/', community_views.alumniBatchGroups, name='group_view'),
    path('', home_views.homeviews, name='home'),
    path('h/',home_views.userviews, name = 'userview'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        alumni.activate_account, name='activate'),
    path('account/activate',alumni.resend_mail, name='reactivate'),
    path('ajax/load-years/', alumni.load_endyear, name='ajax_load_years'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        }),
    ]
urlpatterns += staticfiles_urlpatterns()
