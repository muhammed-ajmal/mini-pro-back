from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import os
from django.contrib.auth import get_user_model
from account.models import Alumni
User = get_user_model()
# Create your models here.


JOB_TYPES = [
    ('FT','Full Time'),
    ('PT','Part Time'),
    ('IN', 'Intern'),
    ('CN', 'Contract'),

]

APPL_STATUS =[
('APP','Approved'),
('PED','Pending'),
]
def user_resume_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    timenow = timezone.now()
    return 'profile/{userid}/resume/{basename}{time}{ext}'.format(
        userid=instance.applicant.id, basename=basefilename,
        time=timenow.strftime("%Y%m%d%H%M%S"), ext=file_extension)



class Job(models.Model):
    posted_by = models.ForeignKey(Alumni, related_name='jobs_author',
                                on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)
    last_date = models.DateField(blank=True, null=False)
    req_skills = models.CharField(max_length=100, null=True, blank=True)
    job_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500, blank=True, default="ND")
    company_name = models.CharField(max_length=100, null=True, blank=True)
    job_type = models.CharField(max_length=3,choices=JOB_TYPES,default='FT')
    location = models.CharField(max_length=500, null=True, blank=True)
    workexp_req = models.CharField(max_length=1000, null=True, blank=True)
    base_salary = models.CharField(max_length=100, null=True, blank=True)
    questions_to_applicants = models.TextField(max_length=1000, null=True, blank=True)
    def __str__(self):
        return self.job_name

class Application(models.Model):
    applicant = models.ForeignKey(User, related_name='job_applicant',
                    blank=True, null=True, on_delete=models.SET_NULL)
    applying_job = models.ForeignKey(Job, related_name='applied_job',
                    blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    resume = models.FileField(upload_to=user_resume_path)
    contact_regex = RegexValidator(regex=r'^[0-9]{10}$', message="10 digits only ")
    contact = models.CharField(validators=[contact_regex], max_length=10, blank=False, default='')
    email = models.EmailField(max_length=254)
    answers_to_employer = models.TextField(max_length=500, blank=True, default="ND")
    questions_to_employer = models.TextField(max_length=500, blank=True, default="ND")
    answers_to_applicants =  models.TextField(max_length=500, blank=True, default="ND")
    application_status = models.CharField(max_length=3,choices=APPL_STATUS,default='PED')
    def __str__(self):
        return self.name
