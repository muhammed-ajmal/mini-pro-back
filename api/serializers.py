from django.contrib.auth import get_user_model
from rest_framework import serializers
from account.models import Alumni,User,AlumniDB,CourseCompletion,AlumniProfile
from account.choices import BRANCH , YEARSSTART, yearsend
from account.utils import OptionalChoiceField
from django.core.validators import RegexValidator
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from datetime import datetime


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
        user.save()
        Alumni.objects.create(user=user, **alumni_user)
        return user

class ActivateAccount(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data['email']

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
