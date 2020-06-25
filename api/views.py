from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from api.serializers import CreateUserSerializer, ActivateAccount, AccountBatchSerializer,AccountBatchCreate,AuthTokenSerializer,ManuelVerificationSerializers
from account.models import Alumni,User,AlumniDB,CourseCompletion,AlumniProfile,ManuelVerification
from api.serializers import SMSVerificationSerializer,VerifySMSTokenSerializer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from account.token_generator import account_activation_token
from django.core.mail import EmailMessage
from rest_framework.decorators import authentication_classes, permission_classes
import json
from account.choices import BRANCH , YEARSSTART, yearsend,BRANCH_JSON,JOB_TYPES_JSON

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.db.models import Q

from django.conf import settings
from authy.api import AuthyApiClient

from rest_framework import generics
from api.serializers import ProfileCreateOrUpdateSerializers,UserSearchSerializer
from api.serializers import CreateJobSerializer
from api.serializers import JobListSerializer,ApplyJobSerializer
from jobs.models import Job,Application
authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)

resetpassword = PasswordResetTokenGenerator()

class ObtainAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

def sendmail(self,request,user,template,token,email_subject):
    current_site = get_current_site(request)
    message = render_to_string(template, {
    'user': user,
    'domain': current_site.domain,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'token': token,
    })
    #'token': account_activation_token.make_token(user),
    to_email = user.email
    email = EmailMessage(email_subject, message, to=[to_email],from_email='alumni@cucek.in')
    email.send()

class CreateUserAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # We create a token than will be used for future auth
        user=serializer.instance
        token = account_activation_token.make_token(user)
        template = 'verify/mail/activate_account_mail.html'
        email_subject = 'Activate Your Acc'
        sendmail(self,request,user,template,token,email_subject)
        print('send message')
        create_message = {"message": "Your account is created successfully now open the actvtn mail, which we already send and activate the account"}
        return Response(
            {**serializer.data, **create_message},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CreateAccountBatchAPIView(CreateAPIView):
    serializer_class = AccountBatchCreate
    permission_classes = [AllowAny]



class ManuelVerificationAPIView(CreateAPIView):
    serializer_class = ManuelVerificationSerializers
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        if ManuelVerification.objects.filter(alumni=alumni,verify_status='ND').exists():
            x = ManuelVerification.objects.get(alumni=alumni)
            x.delete()
        alumni.verification_file = request.data['verification_file']
        alumni.save()
        verify = ManuelVerification.objects.create(alumni=alumni,verify_status='PD')
        message = {
            "alumni" : verify.alumni.user.username,
            "verify_status": verify.verify_status,
            "request_date": verify.request_date,
            "verification_file":alumni.verification_file.path
        }
        return Response(
            {**serializer.data,**message},
            status=status.HTTP_201_CREATED
            )
class LogoutUserAPIView(APIView):
    queryset = get_user_model().objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)



class ResetAccountPassword(CreateAPIView):
    serializer_class =ActivateAccount
    permission_classes = [AllowAny]

    def post(self,request, *args, **kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data['email'])
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user == None :
            pass
        else:
            token = resetpassword.make_token(user)
            template = 'verify/mail/reset_account_password_mail.html'
            email_subject = 'Reset Your Alumni Acc. Password'
            sendmail(self,request,user,template,token,email_subject)
            print('send message')
        content = {'message': 'if you are a registerd user, then you will recieve a mail with password reset link in few minutes!'}
        return Response({**serializer.data, **content},status=status.HTTP_201_CREATED)

class ActivateAccount(CreateAPIView):
    serializer_class =ActivateAccount
    permission_classes = [AllowAny]

    def post(self,request, *args, **kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data['email'])
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user == None :
            pass
        elif user.is_active == False :
            token = account_activation_token.make_token(user)
            template = 'verify/mail/activate_account_mail.html'
            email_subject = 'Activate Your Acc'
            sendmail(self,request,user,template,token,email_subject)
            print('send message')

        content = {'message': 'If your mail id matches with our records and Your account is not activated,then you will recieve a mail asap!'}
        return Response({**serializer.data, **content},status=status.HTTP_201_CREATED)

class SMSVerifyAccount(CreateAPIView):
    serializer_class =SMSVerificationSerializer
    permission_classes = [AllowAny]

    def post(self,request, *args, **kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        authy_api.phones.verification_start(
                alumni.contact,
                '+91',
                via='sms'
            )
        content = {'message': 'sms has been send!'}
        return Response({**serializer.data, **content},status=status.HTTP_201_CREATED)

class SMSVerifyToken(CreateAPIView):
    serializer_class =VerifySMSTokenSerializer
    permission_classes = [AllowAny]

    def post(self,request, *args, **kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        verification = authy_api.phones.verification_check(
                alumni.contact,
                '+91',
                request.data['sms_token']
            )
        if verification.ok():
            if AlumniDB.objects.filter(contact=alumni.contact).exists():
                alumni.verify_status = True
                alumni.save()
                message = {
                 'status': 'verified'
                }
            else:
                message = {
             'status': 'notverified'
             }
        else:
            message = {
                'status': 'failed'
            }
        return Response({**serializer.data, **message},status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_userprofile(request):
    if request.method == 'GET':
        message = {
                "username" : request.user.username,
                "is_alumni" : request.user.is_alumni,
                "is_student" : request.user.is_student,
                "is_admin": request.user.is_admin
            }
        return Response(message)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_userdetails(request,token):
    if request.method == 'GET':
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        if user.is_alumni:
            alumni = get_object_or_404(Alumni.objects.all(), user=user)
            message = {
            "username" : user.username,
                "is_alumni" : user.is_alumni,
                "is_student" : user.is_student,
                "is_admin": user.is_admin,
                "verify_status": alumni.verify_status
            }
        else:
            message = {
                "username" : user.username,
                "is_alumni" : user.is_alumni,
                "is_student" : user.is_student,
                "is_admin": user.is_admin
            }
        return Response(message)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def account_batch(request):
    if request.method == 'GET':
        batchs = CourseCompletion.objects.all()
        serializer = AccountBatchSerializer(batchs, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def account_department(request):
    if request.method == 'GET':
        return Response(BRANCH_JSON)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def jobs_types(request):
    if request.method == 'GET':
        return Response(JOB_TYPES_JSON)


class ProfileCreateOrUpdateAPIView(CreateAPIView):
    serializer_class = ProfileCreateOrUpdateSerializers
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]
    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data.pop('token')
        key = get_object_or_404(Token.objects.all(), key=token[0])
        user = key.user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        if AlumniProfile.objects.filter(alumni=alumni).exists():
            profile = AlumniProfile.objects.get(alumni=alumni)
            profile.profile_pic = request.data['profile_pic']
            if 'skills' in request.data:
                profile.skills = request.data['skills']
            if 'bio' in request.data:
                profile.bio = request.data['bio']
            if 'work' in request.data:
                profile.work = request.data['work']
            if 'organization' in request.data:
                profile.organization = request.data['organization']
            if 'linkedin' in request.data:
                profile.linkedin = request.data['linkedin']
            if 'twitter' in request.data:
                profile.twitter = request.data['twitter']
            if 'facebook' in request.data:
                profile.facebook = request.data['facebook']
            if 'private' in request.data:
                profile.private = request.data['private']
            profile.save()
            if 'csrfmiddlewaretoken' in request.data:
                request.data.pop('csrfmiddlewaretoken')
            request.data.pop('profile_pic')
            message = {
            "alumni":"updated"
            }
        else:
            profile = AlumniProfile.objects.create(alumni=alumni)
            profile.profile_pic = request.data['profile_pic']
            if 'skills' in request.data:
                profile.skills = request.data['skills']
            if 'bio' in request.data:
                profile.bio = request.data['bio']
            if 'work' in request.data:
                profile.work = request.data['work']
            if 'organization' in request.data:
                profile.organization = request.data['organization']
            if 'linkedin' in request.data:
                profile.linkedin = request.data['linkedin']
            if 'twitter' in request.data:
                profile.twitter = request.data['twitter']
            if 'facebook' in request.data:
                profile.facebook = request.data['facebook']
            if 'private' in request.data:
                profile.private = request.data['private']
            profile.save()
            message = {
            "alumni":"created"
            }
        return Response(
            {**serializer.data,**message},
            status=status.HTTP_201_CREATED
            )


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_alumniprofile(request,token):
    if request.method == 'GET':
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        if user.is_alumni:
            current_site = get_current_site(request)
            alumni = get_object_or_404(Alumni.objects.all(), user=user)
            if not AlumniProfile.objects.filter(alumni=alumni).exists():
                AlumniProfile.objects.create(alumni=alumni)
            profile = AlumniProfile.objects.get(alumni=alumni)
            message = {
                "username":user.username,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "profile_pic" : "https://" + current_site.domain + profile.profile_pic.url,
                "bio" : profile.bio,
                "work": profile.work,
                "organization" : profile.organization,
                "skills" : profile.skills,
                "linkedin":profile.linkedin,
                "twitter":profile.twitter,
                "facebook":profile.facebook,
                "private":profile.private
            }
        else:
            message = {
                "username" : user.username,
                "is_alumni" : user.is_alumni,
                "is_student" : user.is_student,
                "is_admin": user.is_admin
            }
        return Response(message)


class UserSearchList(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        term = self.kwargs['term']
        return User.objects.filter(Q(first_name__icontains = term) | Q(last_name__icontains = term) | Q(username__icontains = term))


class UsersList(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return User.objects.filter(is_alumni=True)

class UsersByUsername(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        username = self.kwargs['username']
        return User.objects.filter(username=username)

class CreateJobAPIView(CreateAPIView):
    serializer_class = CreateJobSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        create_message = {"message": "created"}
        return Response(
            {**create_message},
            status=status.HTTP_201_CREATED,
        )
class JobList(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return Job.objects.all()

class JobDetailView(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        id = self.kwargs['id']
        return Job.objects.filter(id=id)
        
class EmployerJobList(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):

        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        token = self.kwargs['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return Job.objects.filter(posted_by=alumni)

def sendjobmail(self,request,user,template,email_subject,object,email):
    current_site = get_current_site(request)
    message = render_to_string(template, {
    'user': user,
    'job': object,
    })
    #'token': account_activation_token.make_token(user),
    to_email = user.email
    email1 = EmailMessage(email_subject, message, to=[to_email],from_email='alumni@cucek.in')
    email1.send()
    email2 = EmailMessage(email_subject, message, to=[email],from_email='alumni@cucek.in')
    email2.send()
class ApplyJobAPIView(CreateAPIView):
    serializer_class = ApplyJobSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        create_message = {"message": "created"}
        token = request.data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        user = key.user
        template = 'jobs/mail/job_applied.html'
        job = Job.objects.get(id=request.data['applying_job'])
        email_subject = 'You applied for a Job : ' + job.job_name
        email = request.data['email']
        sendjobmail(self,request,user,template,email_subject,job,email)
        request.data.pop('resume')
        return Response(
            {**create_message,**request.data},
            status=status.HTTP_201_CREATED,
        )

obtain_auth_token = ObtainAuthToken.as_view()
