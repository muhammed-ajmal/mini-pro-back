from django.contrib import admin
from .models import ReferralRequest
# Register your models here.
class ReferralRequestAdmin(admin.ModelAdmin):
    list_display = ('request_from','request_to','request_note')




admin.site.register(ReferralRequest,ReferralRequestAdmin)
