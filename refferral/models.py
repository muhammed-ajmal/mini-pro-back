from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import os
from django.contrib.auth import get_user_model
from account.models import Alumni,User

REFERRAL_STATUS = [
    ('PD','PENDING'),
    ('SH', 'SHORTLIST'),
    ('DL','DELETE')
]

class ReferralRequest(models.Model):
    request_to =models.ForeignKey(User, related_name='referral_request_to',
                                on_delete=models.CASCADE)
    request_from = models.ForeignKey(User, related_name='referral_request_from',
                                on_delete=models.CASCADE)
    request_note = models.TextField(max_length=500, blank=True, default="ND")
    referral_status = models.CharField(max_length=8,choices=REFERRAL_STATUS,default='PD')
    notes_to_requester = models.TextField(max_length=500, blank=True, default="PD")

    def __str__(self):
        return self.request_from.username + " to " + self.request_to.username
