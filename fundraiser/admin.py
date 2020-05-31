from django.contrib import admin
from .models import FundRaiserEvent,Transaction
# Register your models here.
class FundRaiserEventAdmin(admin.ModelAdmin):
    list_display = ('event_name','target_amount','raised_amount','created_on','created_by')

class TransactionAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Transaction._meta.get_fields()]
    list_display = ('made_by','event','made_on','amount','order_id','checksum','txn_status')

admin.site.register(FundRaiserEvent,FundRaiserEventAdmin)
admin.site.register(Transaction,TransactionAdmin)
