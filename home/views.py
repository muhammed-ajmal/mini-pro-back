from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from account.models import Alumni
# Create your views here.
def homeviews(request):
    return render(request, 'home.html')

@login_required
@transaction.atomic
def userviews(request):
    if request.user.is_alumni:
        alumni = Alumni.objects.get(user=request.user)
        return render(request, 'dash/dashboard.html',{'alumni':alumni})

    return render(request, 'home.html')
