from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime
from userdb.models import AlumniDB
from account.choices import BRANCH ,VERIF_STATUS#choice file
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import os

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    timenow = timezone.now()
    return 'profile/{userid}/{basename}{time}{ext}'.format(userid=instance.alumni.user.id, basename=basefilename, time=timenow.strftime("%Y%m%d%H%M%S"), ext=file_extension)
def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    timenow = timezone.now()
    return 'profile/{userid}/verify/{basename}{time}{ext}'.format(userid=instance.user.id, basename=basefilename, time=timenow.strftime("%Y%m%d%H%M%S"), ext=file_extension)

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_alumni = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

class CourseCompletion(models.Model):
    start = models.DateField(blank=True, null=False)
    end = models.DateField(blank=True, null=False)
    number_of_students = models.IntegerField(default=300)
    number_of_graduates = models.IntegerField(default=0)
    number_of_placed = models.IntegerField(default=0)

    def clean(self):
        duration = self.end.year - self.start.year
        if duration < 0 or duration != 4:
            raise ValidationError({
    'end': ValidationError('Period Must Be 4 Years'),
    })
        if CourseCompletion.objects.filter(start__year=self.start.year).exists():
            raise ValidationError({
    'start': ValidationError('Your Batch Already Exists'),
    'end': ValidationError('GoBack and Continue to signup'),
    })
    class Meta:
        verbose_name_plural = "Course Periods"
        ordering = ['-start']

    def __str__(self):
        return '%s-%s' % (self.start.year, self.end.year)


class Alumni(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=3,choices=BRANCH)
    batch = models.ForeignKey(CourseCompletion, on_delete=models.SET_NULL,null=True)
    contact_regex = RegexValidator(regex=r'^[0-9]{10}$', message="10 digits only ")
    contact = models.CharField(validators=[contact_regex], max_length=10, blank=False, default='',help_text=' your registerd phone number with university if availabe ,your number help us to auto verify your profile')
    reg_date = models.DateTimeField(default=timezone.now)
    verify_status = models.BooleanField(default=False)
    verification_file = models.ImageField(upload_to=file_directory_path, default='File.png',help_text="Verification ID")

    class Meta:
        ordering = ['batch']

    def clean(self):
        print(self.user.email)
        if AlumniDB.objects.filter(email=self.user.email).exists():
            self.verify_status = True
        else:
            pass

    def publish(self):
        if AlumniDB.objects.filter(email=self.user.email).exists():
            self.verify_status = True
        else:
            pass
        self.reg_date = timezone.now()
        self.save()

    def __str__(self):
        return self.user.username

class ManuelVerification(models.Model):
    alumni = models.OneToOneField(Alumni, on_delete=models.CASCADE, primary_key=True)
    verify_status = models.CharField(max_length=2,choices=VERIF_STATUS)
    #verification_file = models.ImageField(upload_to=user_directory_path, default=,help_text="Profile Picture")
    request_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Manuel Verifications"
        ordering = ['-request_date']
    def __str__(self):
        return self.alumni.user.username

class AlumniProfile(models.Model):
    alumni = models.OneToOneField(Alumni,on_delete=models.CASCADE,primary_key=True)
    profile_pic = models.ImageField(upload_to=user_directory_path, default='profile.png',help_text="Profile Picture")
    bio = models.TextField(max_length=500, blank=True, default="ND")
    skills = models.CharField(max_length=100, blank=True, default="Analytical Skill")
    work = models.CharField(max_length=30, blank=True, default="Developer", help_text="eg:- Web Developer ,s/w Architect, s/m admin...etc")
    organization = models.CharField(max_length=100, blank=True, default="XYZ Co")
    linkedin = models.URLField(max_length=200, blank=True, default="https://www.linkedin.com/in/username/")
    twitter = models.URLField(max_length=200, blank=True, default="https://twitter.com/username")
    facebook = models.URLField(max_length=200, blank=True, default="https://facebook.com/username")
    private = models.BooleanField(default=True, help_text="<b>Make Your Profile Private</b>")

    def __str__(self):
        return self.alumni.user.username
