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


from api.serializers import CreateUserSerializer, ActivateAccount, AccountBatchSerializer,AccountBatchCreate,AuthTokenSerializer
from account.models import Alumni,User,AlumniDB,CourseCompletion,AlumniProfile

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from account.token_generator import account_activation_token
from django.core.mail import EmailMessage
from rest_framework.decorators import authentication_classes, permission_classes
import json
from account.choices import BRANCH , YEARSSTART, yearsend, BRANCH_JSON

from django.contrib.auth.tokens import PasswordResetTokenGenerator

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
        token = Token.objects.create(user=serializer.instance)
        token_data = {"token": token.key}
        return Response(
            {**serializer.data, **token_data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CreateAccountBatchAPIView(CreateAPIView):
    serializer_class = AccountBatchCreate
    permission_classes = [AllowAny]


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

obtain_auth_token = ObtainAuthToken.as_view()
