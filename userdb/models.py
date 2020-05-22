from django.db import models
from django.utils.html import escape, mark_safe
from django.core.validators import RegexValidator
from django.utils import timezone
# Create your models here.
class AlumniDB(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(help_text='mail@cucek.in',unique=True)
    contact_regex = RegexValidator(regex=r'^[0-9]{10}$', message="10 digits only ")
    contact = models.CharField(validators=[contact_regex], max_length=10, blank=False,help_text='eg:9876543210',unique=True)
    batch_regex = RegexValidator(regex=r'^\d{4}-\d{4}$', message="Should follow the format eg: 2017-2021 ")
    batch =  models.CharField(validators=[batch_regex], max_length=9, blank=False, default='',help_text='eg:2017-2021')

    def __str__(self):
        return self.first_name + " "+self.last_name
