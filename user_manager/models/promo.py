import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django_extensions.db.models import TimeStampedModel
from model_utils.choices import Choices


def a_month_from_now():
    return datetime.date.today() + relativedelta(months=+1)


class PromoCode(TimeStampedModel):
    code = models.CharField(max_length=20)
    TYPE_CHOICES = Choices('percent', 'amount', 'first-percent', 'first-amount')
    type = models.CharField(choices=TYPE_CHOICES, max_length=50)
    discount = models.PositiveSmallIntegerField()
    expiry_date = models.DateField(default=a_month_from_now)
