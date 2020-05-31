from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

STATUS = [
    ('init', 'Initiated'),
    ('success', 'Success.'),
    ('failed', 'Failed'),
    ('refunded', 'Refund'),
]
class FundRaiserEvent(models.Model):
    created_by = models.ForeignKey(User, related_name='events',
                                on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    event_name = models.CharField(max_length=100, null=True, blank=True)
    target_amount = models.IntegerField()
    description = models.CharField(max_length=100, null=True, blank=True)
    raised_amount = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return self.event_name

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions',
                                on_delete=models.CASCADE)
    event = models.ForeignKey(FundRaiserEvent, related_name='fund_event',
                                on_delete=models.SET_NULL,null=True)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=1000, null=True, blank=True)
    checksum = models.CharField(max_length=1000, null=True, blank=True)
    txn_status = models.CharField(max_length=8,choices=STATUS,default='init')

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
