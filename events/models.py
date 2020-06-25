from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import os
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
EVENT_STATUS = [
    ('PB','PUBLIC EVENT'),
]



class EventsByMentor(models.Model):
    conducted_by = models.ForeignKey(User, related_name='event_author',
                                on_delete=models.CASCADE)
    posted_on = models.DateField(auto_now_add=True)
    event_date = models.DateField()
    event_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500, blank=True, default="ND")
    event_status = models.CharField(max_length=8,choices=EVENT_STATUS,default='PB')
    location = models.CharField(max_length=500, null=True, blank=True)
    special_req = models.CharField(max_length=1000, null=True, blank=True)
    def __str__(self):
        return self.event_name

class EventRegistration(models.Model):
    event = models.ForeignKey(EventsByMentor, related_name='event_registration',
                    blank=True, null=True, on_delete=models.SET_NULL)
    attendee = models.ForeignKey(User, related_name='event_attendee',
                    blank=True, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.attendee.username
