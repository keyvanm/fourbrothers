import datetime
from datetime import timedelta

from django.db import models
from django_extensions.db.models import TimeStampedModel
from model_utils.choices import Choices


def thirty_days_from_now():
    return datetime.date.today() + timedelta(days=30)


class PromoCode(TimeStampedModel):
    code = models.CharField(max_length=20)
    TYPE_CHOICES = Choices('percent', 'amount', 'first-percent', 'first-amount')
    type = models.CharField(choices=TYPE_CHOICES, max_length=50)
    discount = models.PositiveSmallIntegerField()
    expiry_date = models.DateField(default=thirty_days_from_now)
