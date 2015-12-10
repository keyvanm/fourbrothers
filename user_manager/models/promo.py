import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

from django.db import models
from django_extensions.db.models import TimeStampedModel
from model_utils.choices import Choices


def a_month_from_now():
    return datetime.date.today() + relativedelta(months=+1)


class InvalidPromotionException(ValidationError):
    pass


class Promotion(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    TYPE_CHOICES = Choices('percent', 'amount', 'first-percent', 'first-amount')
    type = models.CharField(choices=TYPE_CHOICES, max_length=50)
    discount = models.PositiveSmallIntegerField()
    expiry_date = models.DateField(default=a_month_from_now)

    @property
    def description(self):
        if self.type == 'percent':
            return "{}% off your purchase".format(self.discount)
        if self.type == 'amount':
            return "C${} off your purchase".format(self.discount)
        if self.type == 'first-percent':
            return "{}% off your first purchase".format(self.discount)
        if self.type == 'first-amount':
            return "C${} off your first purchase".format(self.discount)

    def __unicode__(self):
        return "{} | {}".format(self.code, self.description)

    @classmethod
    def get_promo(cls, promo_code, appt):
        try:
            promo = Promotion.objects.get(code=promo_code)
        except Promotion.DoesNotExist:
            raise InvalidPromotionException("Invalid promo code")
        if promo in appt.user.profile.promos_used.all():
            raise InvalidPromotionException("You have already used this promotion")
        if (promo.type == 'first-percent' or promo.type == 'first-amount') and not appt.is_first_paid_appt():
            raise InvalidPromotionException('You can only use this promotion on your first purchase')
        return promo

    def get_discount_on_price(self, price):
        # price = Decimal(price)
        if self.type == 'percent' or self.type == 'first-percent':
            return Decimal(price * self.discount / 100)
        if self.type == 'amount' or self.type == 'first-amount':
            if price - self.discount > 0:
                return Decimal(self.discount)
            else:
                return Decimal(price)

    def get_discount_on_appt(self, appt):
        if self in appt.user.profile.promos_used.all():
            raise InvalidPromotionException("You have already used this promotion")
        if (self.type == 'first-percent' or self.type == 'first-amount') and not appt.is_first_paid_appt():
            raise InvalidPromotionException('You can only use this promotion on your first purchase')

        price = appt.get_price()
        return Decimal(self.get_discount_on_price(price))
