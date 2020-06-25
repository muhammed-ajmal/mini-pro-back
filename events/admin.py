from django.contrib import admin
from .models import EventsByMentor,EventRegistration
# Register your models here.
class EventsByMentorAdmin(admin.ModelAdmin):
    list_display = ('event_name','event_date','description','location','special_req','event_status')

class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event','attendee')

admin.site.register(EventsByMentor,EventsByMentorAdmin)
admin.site.register(EventRegistration,EventRegistrationAdmin)
