from django.conf.urls import url
from .views import CreateUserAPIView, LogoutUserAPIView,account_batch, account_department,CreateAccountBatchAPIView,obtain_auth_token
from .views import ActivateAccount,ResetAccountPassword, ManuelVerificationAPIView,get_userdetails
from .views import SMSVerifyAccount,SMSVerifyToken,get_userprofile,get_alumniprofile
from .views import ProfileCreateOrUpdateAPIView,UserSearchList,CreateJobAPIView
from .views import UsersList, UsersByUsername,ApplyJobAPIView
from .views import jobs_types,JobList,EmployerJobList
from .views import JobDetailView,ApplicationList,ApplicationDetail

from .views import CreateEventAPIView,EventList,CreateStudentUserAPIView,student_batch

from .views import CreateReferralRequestAPIView,ReferralRequestListTo,ReferralRequestListFrom
urlpatterns = [
    url(r'^auth/login/$',
        obtain_auth_token,
        name='auth_user_login'),
    url(r'^auth/register/$',
        CreateUserAPIView.as_view(),
        name='auth_user_create'),
    url(r'^auth/register/student/$',
        CreateStudentUserAPIView.as_view(),
        name='auth_user_student_create'),
    url(r'^auth/logout/$',
        LogoutUserAPIView.as_view(),
        name='auth_user_logout'),
    url(r'^auth/account/reset$', ActivateAccount.as_view()),
    url(r'^auth/account/password/reset$', ResetAccountPassword.as_view()),
    url(r'^auth/account/create/batches/$',CreateAccountBatchAPIView.as_view()),
    url(r'^auth/account/get/batches/$', account_batch),
    url(r'^auth/account/get/batches/student/$', student_batch),
    url(r'^auth/account/get/departments/$', account_department),
    url(r'^auth/account/get/usertype/(?P<token>[\w.@+-]+)/$',get_userdetails),
    url(r'^auth/account/verify/alumni/manuel/$', ManuelVerificationAPIView.as_view()),
    url(r'^auth/account/verify/alumni/sms/$', SMSVerifyAccount.as_view()),
    url(r'^auth/account/verify/alumni/sms/check/$', SMSVerifyToken.as_view()),
    url(r'^auth/get/data/$',get_userprofile),
    url(r'^profile/update/',ProfileCreateOrUpdateAPIView.as_view()),
    url(r'^get/profile/(?P<token>[\w.@+-]+)/$',get_alumniprofile),
    url(r'^user/search/(?P<term>[\w.@+-]+)/$', UserSearchList.as_view()),
    url(r'^user/profile/get/(?P<username>[\w.@+-]+)/$', UsersByUsername.as_view()),
    url(r'^user/list/$', UsersList.as_view()),
    url(r'^get/jobs/$', JobList.as_view()),
    url(r'^get/job/(?P<id>[\w.@+-]+)/detail/$', JobDetailView.as_view()),
    url(r'^job/create/$', CreateJobAPIView.as_view()),
    url(r'^job/get/types/$', jobs_types),
    url(r'^get/jobs/byemployer/(?P<token>[\w.@+-]+)/$', EmployerJobList.as_view()),
    url(r'^job/apply/$', ApplyJobAPIView.as_view()),
    url(r'^get/job/(?P<id>[\w.@+-]+)/applications/$', ApplicationList.as_view()),
    url(r'^get/job/(?P<id>[\w.@+-]+)/application/$', ApplicationDetail.as_view()),
    url(r'^event/create/$', CreateEventAPIView.as_view()),
    url(r'^get/events/$', EventList.as_view()),
    url(r'^ref/create/$', CreateReferralRequestAPIView.as_view()),
    url(r'^get/refrequest/(?P<token>[\w.@+-]+)/requested/$', ReferralRequestListTo.as_view()),
    url(r'^get/refrequest/(?P<token>[\w.@+-]+)/recieved/$', ReferralRequestListFrom.as_view())

]
