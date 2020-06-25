from django.contrib.auth import get_user_model
from rest_framework import serializers
from account.models import Alumni,User,AlumniDB,CourseCompletion,AlumniProfile,ManuelVerification
from account.choices import BRANCH , YEARSSTART, yearsend
from account.utils import OptionalChoiceField
from django.core.validators import RegexValidator
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from django.db.models.fields import DateField
from datetime import datetime
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token


from jobs.models import Job,Application

from refferral.models import ReferralRequest


from events.models import EventRegistration,EventsByMentor



class AuthTokenSerializer(AuthTokenSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_active:
                msg ={'notactivated':'Either activate or request for new account activation link.'}
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class AlumniUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alumni
        fields = ('department', 'batch', 'contact')
class CreateUserSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True,
                                     style={'input_type': 'password'})
    email = serializers.EmailField()
    alumni = AlumniUserSerializer(required=True)
    def validate(self, data):
        email = data['email']
        username = data['username']
        password = data.get('password')
        errors = dict()
        try:
            validators.validate_password(password=password, user=User)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already taken")
        if errors:
             raise serializers.ValidationError(errors)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        contact = data['alumni']['contact']
        if Alumni.objects.filter(contact=contact).exists():
            raise serializers.ValidationError("contact already taken")
        return data

    class Meta:
        model = User
        fields = ('username', 'password','email', 'first_name', 'last_name','alumni')
        write_only_fields = ('password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active',)

    def create(self, validated_data):
        alumni_user = validated_data.pop('alumni')
        user = super(CreateUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.is_alumni = True
        user.is_active = False
        user.save()
        Alumni.objects.create(user=user, **alumni_user)
        return user

class ActivateAccount(serializers.Serializer):
    email = serializers.EmailField()
    def save(self):
        email = self.validated_data['email']


class ManuelVerificationSerializers(serializers.ModelSerializer):
    token = serializers.CharField()
    class Meta:
        model = Alumni
        fields = ('verification_file','token')

    def get_user(self,data):
        token = data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        user = self.get_user(data).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        if ManuelVerification.objects.filter(alumni=alumni,verify_status='PD').exists():
            raise serializers.ValidationError({'token':"request already exists"})
        return data
    def save(self):
        token = self.validated_data['token']
        verification_file = self.validated_data['verification_file']
class AccountBatchCreate(serializers.ModelSerializer):
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=True)
    class Meta:
        model = CourseCompletion
        fields = ('start', 'end')
    def validate(self,data):
        if data['start'].year > datetime.now().year-4:
            raise serializers.ValidationError({
     'start': 'Only for Alumnis',
     })
        duration = data['end'].year - data['start'].year
        if duration < 0 or duration != 4:
            raise serializers.ValidationError({
    'end': 'Period Must Be 4 Years',
    })
        if CourseCompletion.objects.filter(start__year=data['start'].year).exists():
            raise serializers.ValidationError({
    'start': 'Your Batch Already Exists',
    'end': 'GoBack and Continue to signup',
    })
        return data

class AccountBatchSerializer(serializers.ModelSerializer):
    batch = serializers.SerializerMethodField()
    def get_batch(self, obj):
        return '{}-{}'.format(obj.start.year, obj.end.year)
    class Meta:
        model = CourseCompletion
        fields = ('id','batch')

class SMSVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()
    def get_user(self,data):
        token = data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        user = self.get_user(data).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return data
    def save(self):
        token = self.validated_data['token']

class VerifySMSTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    sms_token = serializers.CharField()
    def get_user(self,data):
        token = data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        user = self.get_user(data).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return data
    def save(self):
        token = self.validated_data['token']
        sms_token = self.validated_data['sms_token']


class ProfileCreateOrUpdateSerializers(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    token = serializers.CharField()
    class Meta:
        model = AlumniProfile
        fields = ('profile_pic','bio', 'work','organization','skills','linkedin','twitter','facebook','private','token')

    def get_user(self,data):
        token = data['token']
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        print(data)
        user = self.get_user(data).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return data
    def save(self):
        profile_pic = self.validated_data['profile_pic']
        bio = self.validated_data['bio']
        work= self.validated_data['work']
        organization= self.validated_data['organization']
        skills= self.validated_data['skills']
        linkedin= self.validated_data['linkedin']
        twitter= self.validated_data['twitter']
        facebook= self.validated_data['facebook']
        private= self.validated_data['private']






#view list


class AlumniProfileUserSearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AlumniProfile
        fields = ('profile_pic', 'bio', 'work','organization','skills','linkedin','twitter','facebook','private')
class CourseCompletionSerailzer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CourseCompletion
        fields = ('start','end')
class AlumniUserSearchSerializer(serializers.HyperlinkedModelSerializer):
    batch = CourseCompletionSerailzer()
    alumniprofile = AlumniProfileUserSearchSerializer()
    class Meta:
        model = Alumni
        fields = ('department','batch','alumniprofile')

class UserSearchSerializer(serializers.ModelSerializer):
    alumni = AlumniUserSearchSerializer()
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','alumni')


#Job
class CreateJobSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    class Meta:
        model = Job
        fields = ('job_name','company_name','description','job_type','location','workexp_req','base_salary','questions_to_applicants','last_date','req_skills','token')

    def get_user(self,token):
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        print(data)
        user = self.get_user(data['token']).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return data
    def create(self, validated_data):
        token = validated_data['token']
        user = self.get_user(token).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        validated_data.update({'posted_by':alumni})
        token = validated_data.pop('token')
        print(validated_data)
        job = super(CreateJobSerializer, self).create(validated_data)
        job.save()
        #validated_data.update({'token':token})
        return job

class JobListSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    def get_job_type(self,obj):
        return obj.get_job_type_display()
    def get_creator(self, obj):
        return "%s" % obj.posted_by.user
    class Meta:
        model = Job
        fields = '__all__'


class ApplyJobSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    class Meta:
        model = Application
        fields = ('applying_job','name','resume','contact','email','answers_to_employer','questions_to_employer','token')

    def get_user(self,token):
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        print(data)
        user = self.get_user(data['token']).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        if Application.objects.filter(applying_job=data['applying_job']).filter(applicant=user).exists():
            raise serializers.ValidationError("already applied")
        return data
    def create(self, validated_data):
        token = validated_data['token']
        user = self.get_user(token).user
        validated_data.update({'applicant':user})
        token = validated_data.pop('token')
        print(validated_data)
        apply = super(ApplyJobSerializer, self).create(validated_data)
        apply.save()
        #validated_data.update({'token':token})
        return apply

class ApplicationListSerializer(serializers.ModelSerializer):
    applied_by = serializers.SerializerMethodField()
    linkedin = serializers.SerializerMethodField()
    twitter = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    work = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()
    def get_application_status(self,obj):
        return obj.get_application_status_display()
    def get_applied_by(self, obj):
        return obj.applicant.first_name
    def get_linkedin(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.linkedin
    def get_twitter(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.twitter
    def get_facebook(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.facebook
    def get_bio(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.bio
    def get_work(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.work
    def get_organization(self,obj):
        user = obj.applicant
        alumni = Alumni.objects.get(user=user)
        profile = AlumniProfile.objects.get(alumni=alumni)
        return profile.organization
    class Meta:
        model = Application
        fields = '__all__'

class CreateEventsSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    class Meta:
        model = EventsByMentor
        fields = ('event_name','event_date','description','location','special_req','token')

    def get_user(self,token):
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        print(data)
        user = self.get_user(data['token']).user
        alumni = get_object_or_404(Alumni.objects.all(), user=user)
        return data
    def create(self, validated_data):
        token = validated_data['token']
        user = self.get_user(token).user
        validated_data.update({'conducted_by':user})
        token = validated_data.pop('token')
        print(validated_data)
        event = super(CreateEventsSerializer, self).create(validated_data)
        event.save()
        #validated_data.update({'token':token})
        return event

class EventListSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField()
    def get_event_type(self,obj):
        return obj.get_event_status_display()
    def get_creator(self, obj):
        return "%s" % obj.conducted_by
    class Meta:
        model = EventsByMentor
        fields = '__all__'

class CreateReferralRequestSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    class Meta:
        model = ReferralRequest
        fields = ('request_to','request_note', 'token')

    def get_user(self,token):
        key = get_object_or_404(Token.objects.all(), key=token)
        return key
    def validate(self,data):
        print(data)
        user = self.get_user(data['token']).user
        if ReferralRequest.objects.filter(request_to=data['request_to']).filter(request_from=user).exists():
            raise serializers.ValidationError("request already exists")
        return data
    def create(self, validated_data):
        token = validated_data['token']
        user = self.get_user(token).user
        token = validated_data.pop('token')
        validated_data.update({'request_from':user})
        print(validated_data)
        ref_request = super(CreateReferralRequestSerializer, self).create(validated_data)
        ref_request.save()
        #validated_data.update({'token':token})
        return ref_request

class ReferralRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsByMentor
        fields = '__all__'
