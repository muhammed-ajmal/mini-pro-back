from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from .utils import OptionalChoiceField
from .choices import BRANCH , YEARSSTART, yearsend
from django.core.validators import RegexValidator
from account.models import (Alumni,CourseCompletion,User)
from userdb.models import AlumniDB

from django.utils.safestring import mark_safe

import phonenumbers
from phonenumbers import NumberParseException

class AlumniSignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    batch = forms.ModelChoiceField(
        queryset = CourseCompletion.objects.all(),
        required = True,
        label=mark_safe('Batch <small class="text-muted"> My Batch is missing ? <a href="/signup/add/batch" target="_blank"><i class="fa fa-plus" aria-hidden="true"></i> batch</a> </small>')
    )
    department = OptionalChoiceField(choices=BRANCH)
    contact = forms.CharField(max_length=10,min_length=10, validators=[RegexValidator(regex=r'^[0-9]{10}$', message="10 digits only ")],help_text=' your registerd phone number with university if availabe ,your number help us to auto verify your profile')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','password1','password2','email')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_alumni = True
        user.save()
        if AlumniDB.objects.filter(email=user.email).exists():
            alumni = Alumni.objects.create(user=user,batch=self.cleaned_data.get('batch'),department=self.cleaned_data.get('department'),contact=self.cleaned_data.get('contact'),verify_status=True)
        else:
            alumni = Alumni.objects.create(user=user,batch=self.cleaned_data.get('batch'),department=self.cleaned_data.get('department'),contact=self.cleaned_data.get('contact'))
        return user
class AccountActivationForm(forms.Form):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

class EmailUpdateForm(forms.ModelForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    class Meta:
        model = User
        fields = ('email',)

class UserForm(forms.ModelForm):


    class Meta:
        model = User
        fields = ('first_name', 'last_name','email','username')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = ('contact','batch','department')

class MiscBatchForm(forms.ModelForm):
    start = forms.DateField(widget=forms.SelectDateWidget(years=YEARSSTART))
    end = forms.DateField(widget=forms.SelectDateWidget(years=yearsend(1990)))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end'].queryset = CourseCompletion.objects.none()
    """
    def clean_end(self):
        try:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            x = end.year - start.year
        except(KeyError):
            raise forms.ValidationError("Choose the end year")
        if x != 4 :
            raise forms.ValidationError("The period must be 4 years")
        if CourseCompletion.objects.filter(start__year=start.year).exists():
            raise forms.ValidationError("Your Batch Already exists ")
        else:
            pass
    """
    class Meta:
        model = CourseCompletion
        fields = ('start', 'end')

class AccountActivationPhoneForm(forms.Form):
    country_code = forms.CharField(max_length=3)
    phone_number = forms.CharField(max_length=10)
    via = forms.ChoiceField(
        choices=[('sms', 'SMS'), ('call', 'Call')])

    def clean_country_code(self):
        country_code = self.cleaned_data['country_code']
        if not country_code.startswith('+'):
            country_code = '+' + country_code
        return country_code

    def clean(self):
        data = self.cleaned_data
        phone_number = data['country_code'] + data['phone_number']
        try:
            phone_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(phone_number):
                self.add_error('phone_number', 'Invalid phone number')
        except NumberParseException as e:
            self.add_error('phone_number', e)

class TokenForm(forms.Form):
    token = forms.CharField(max_length=6)
