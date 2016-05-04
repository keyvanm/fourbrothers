from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from model_utils.choices import Choices


class Address(TimeStampedModel):
    address1 = models.CharField(max_length=255, verbose_name="Street Address")
    address2 = models.CharField(max_length=255, blank=True, verbose_name="Apt/Suite/Bldg")
    CITY_CHOICES = Choices(('Toronto', 'Downtown Toronto'), 'Etobicoke', 'Markham', 'North York', 'Scarborough', 'Richmondhill', 'Vaughan')
    city = models.CharField(choices=CITY_CHOICES, max_length=200)
    STATE_CHOICES = Choices('Ontario')
    state = models.CharField(max_length=200, verbose_name='Province', choices=STATE_CHOICES, default='Ontario')
    postal_code = models.CharField(max_length=20, verbose_name="ZIP/Postal Code")
    country = models.CharField(max_length=200, default="Canada")

    def __unicode__(self):
        if self.address2:
            return "{} - {}, {}, {} {}, {}".format(
                self.address2, self.address1, self.city, self.state, self.postal_code.upper(), self.country)
        return "{}, {}, {} {}, {}".format(self.address1, self.city, self.state, self.postal_code.upper(), self.country)

    class Meta:
        verbose_name_plural = "addresses"


class Building(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    address = models.OneToOneField(Address)

    def __unicode__(self):
        return "{} @ {}".format(self.name, self.address.address1)


class BuildingPreScheduledTimeSlot(TimeStampedModel):
    building = models.ForeignKey(Building, related_name="available_slots")
    date = models.DateField()
    TIME_SLOT_CHOICES = (
        ('8am', '8 - 11 AM'),
        ('11am', '11 AM - 2 PM'),
        ('2pm', '2 - 5 PM'),
        ('5pm', '5 - 8 PM'),
    )
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, blank=True)

    def __unicode__(self):
        return "{}, {} @ {}".format(self.date, self.time_slot, self.building.name)


class ParkingLocation(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_set')
    name = models.CharField(max_length=200, verbose_name='Nickname', blank=True )
    address = models.OneToOneField(Address, related_name='%(class)s_set')

    def __unicode__(self):
        return "{}'s {} @ {}".format(self.owner.get_full_name(), self.name, self.address.address1)

    def get_full_name(self):
        return "{} @ {}".format(self.name, self.address.address1)


class PrivateParkingLocation(ParkingLocation):
    pass


class SharedParkingLocation(ParkingLocation):
    building = models.ForeignKey(Building)

    def save(self, *args, **kwargs):
        address = self.building.address
        address.pk = None
        address.save()
        self.address = address
        self.name = self.building.name
        super(SharedParkingLocation, self).save(*args, **kwargs)
