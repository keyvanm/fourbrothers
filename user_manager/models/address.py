from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from model_utils.choices import Choices


class Address(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    TYPE_CHOICES = Choices('home', 'work')
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)

    BLDG_TYPE_CHOICES = Choices('house', 'building')
    building_type = models.CharField(choices=BLDG_TYPE_CHOICES, max_length=20)

    primary = models.BooleanField(default=False)

    address1 = models.CharField(max_length=255, verbose_name="Street Address")
    address2 = models.CharField(max_length=255, blank=True, verbose_name="Apt/Suite/Bldg")
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200, verbose_name='State/Province')
    postal_code = models.CharField(max_length=20, verbose_name="ZIP/Postal Code")
    country = models.CharField(max_length=200)

    def __unicode__(self):
        if self.address2:
            return "{} - {}, {}, {} {}, {}".format(
                self.address2, self.address1, self.city, self.state, self.postal_code.upper(), self.country)
        return "{}, {}, {} {}, {}".format(self.address1, self.city, self.state, self.postal_code.upper(), self.country)

    class Meta:
        verbose_name_plural = "addresses"
