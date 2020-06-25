from django.contrib import admin
from .models import Job,Application
# Register your models here.
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name','last_date','location','posted_by')

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant','applying_job','contact','questions_to_employer')

admin.site.register(Job,JobAdmin)
admin.site.register(Application,ApplicationAdmin)
