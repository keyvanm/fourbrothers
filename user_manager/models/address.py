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


class Building(TimeStampedModel):
    name = models.CharField(max_length=200)
    address = models.OneToOneField(Address)
    next_scheduled_time = models.DateField()
    TIME_SLOT_CHOICES = (
        ('8am', '8 - 11 AM'),
        ('11am', '11 AM - 2 PM'),
        ('2pm', '2 - 5 PM'),
        ('5pm', '5 - 8 PM'),
    )
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, blank=True)
