from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
#send_verification_mail
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from .token_generator import account_activation_token
from django.core.mail import EmailMessage

from ..choices import yearsend
from ..forms import AlumniSignUpForm,AccountActivationForm,UserForm,ProfileForm,EmailUpdateForm,MiscBatchForm,AccountActivationPhoneForm,TokenForm
from ..models import Alumni,User,AlumniDB,CourseCompletion

import requests

from django.conf import settings
from authy.api import AuthyApiClient
authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)

def sendmail(request,user,form):
    current_site = get_current_site(request)
    email_subject = 'Activate Your Acc'
    message = render_to_string('activate_account.html', {
    'user': user,
    'domain': current_site.domain,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'token': account_activation_token.make_token(user),
    })
    to_email = form.cleaned_data.get('email')
    email = EmailMessage(email_subject, message, to=[to_email],from_email='noreply@mg.alumni-cucek.ml')
    email.send()

@login_required
@transaction.atomic
def send_sms(request):
    if request.method == 'POST':
        form = AccountActivationPhoneForm(request.POST,initial={'country_code': '+91','phone_number':request.user.alumni.contact})
        if form.is_valid():
            request.session['phone_number'] = form.cleaned_data['phone_number']
            request.session['country_code'] = form.cleaned_data['country_code']
            authy_api.phones.verification_start(
                form.cleaned_data['phone_number'],
                form.cleaned_data['country_code'],
                via=form.cleaned_data['via']
            )
            return redirect('sms_token_validation')
    else:
        form = AccountActivationPhoneForm(initial={'country_code': '+91','phone_number':request.user.alumni.contact})
    return render (request, 'resend_activation_mail.html',{'form': form} )

@login_required
@transaction.atomic
def sms_token_validation(request):
    if request.method == 'POST':
        form = TokenForm(request.POST)
        if form.is_valid():
            verification = authy_api.phones.verification_check(
                request.session['phone_number'],
                request.session['country_code'],
                form.cleaned_data['token']
            )
            if verification.ok():
                if AlumniDB.objects.filter(contact=request.user.alumni.contact).exists():
                    request.user.alumni.verify_status = True
                    request.user.alumni.save()
                return redirect('userview')
            else:
                for error_msg in verification.errors().values():
                    form.add_error(None, error_msg)
    else:
        form = TokenForm()
    return render(request, 'resend_activation_mail.html', {'form': form})


class AlumniSignUpView(CreateView):
    model = User
    form_class = AlumniSignUpForm
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Alumni'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()
        sendmail(self.request,user,form)
        return render(self.request, 'mail_send.html')
        #return redirect('home')

class AddBatchView(CreateView):
    model = CourseCompletion
    form_class = MiscBatchForm
    template_name = 'add_batch.html'

    def form_valid(self, form):
        batch = form.save()
        batch.save()
        return redirect('signup')
        #return redirect('home')

def resend_mail(request):
    if request.method == 'POST':
        form = AccountActivationForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data.get('email'))
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user == None :
                return render(request, 'reactivation_mail_send.html')
            elif user.is_active == False :
                sendmail(request,user,form)
                return render(request, 'reactivation_mail_send.html')
            else:
                return render(request, 'reactivation_mail_send.html')
    else:
        form = AccountActivationForm()
    return render (request, 'resend_activation_mail.html',{'form': form} )




def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        alumni = Alumni.objects.get(user=user)
        groupname = str(alumni.department)+'-'+str(alumni.batch)
        headers = {
         'Api-Key': settings.DISCOURSE_API,
          'Api-Username': 'dev'
        }
        url = 'https://community.alumni-cucek.ml/admin/groups'
        params = {
        "group[name]": groupname
        }
        resp = requests.post(url, params=params, headers=headers)
        print(resp.text)
        login(request, user)
        #return HttpResponse('Your account has been activate successfully')
        return redirect('userview')
    else:
        return render(request, 'invalid_link.html')

@login_required
@transaction.atomic
def update_email(request):
    try:
        alumni = Alumni.objects.get(user=request.user)
    except(Alumni.DoesNotExist):
        alumni = None
    if  alumni is not None and request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid() :
            user = form.save()
            user.is_active = False
            user.save()
            if AlumniDB.objects.filter(email=request.user.email).exists():
                self.verify_status = True
            else:
                pass
            sendmail(request,user,form)
            return render(request, 'reactivation_mail_send.html')
        else:
            email = form.data['email']
            if email == request.user.email:
                messages.error(request, 'The email is already activated and connected with your account')
                if AlumniDB.objects.filter(email=request.user.email).exists():
                    alumni.verify_status = True
                    alumni.save()
                    messages.error(request, 'The email is verified')
            else :
                messages.error(request, 'The email is already connected with other account')
    else:
        form = EmailUpdateForm(instance=request.user)
    return render (request, 'resend_activation_mail.html',{'form': form} )



@login_required
@transaction.atomic
def update_profile(request):
    try:
        alumni = Alumni.objects.get(user=request.user)
    except(Alumni.DoesNotExist):
        alumni = None
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.alumni)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('userview')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.alumni)
    return render(request, 'dash/profile_update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'alumni':alumni
    })

def load_endyear(request):
    startyear = request.GET.get('start_year')
    print(startyear)
    endyear = yearsend(startyear)
    return render(request, 'hr/endyear_dropdown_list_options.html', {'endyear': endyear})
