from django.conf import settings
from django.db import models

from django_extensions.db.models import TimeStampedModel

from user_manager.models.address import Address, ParkingLocation
from user_manager.models.car import Car


class Appointment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='appointments')
    cars = models.ManyToManyField(Car, through='ServicedCar')
    canceled = models.BooleanField(default=False)

    date = models.DateField(
        # validators=[
        #     MinValueValidator(datetime.date.today())
        # ]
    )
    TIME_SLOT_CHOICES = (
        ('8am', '8 - 11 AM'),
        ('11am', '11 AM - 2 PM'),
        ('2pm', '2 - 5 PM'),
        ('5pm', '5 - 8 PM'),
    )
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    address = models.ForeignKey(ParkingLocation)
    technician = models.ManyToManyField(settings.AUTH_USER_MODEL, limit_choices_to={'profile__type': 'technician'},
                                        related_name='assigned_appts', blank=True)
    GRATUITY_CHOICES = (
        (0, '0%'),
        (5, '5%'),
        (10, '10%'),
        (15, '15%'),
        (20, '20%'),
    )
    gratuity = models.PositiveSmallIntegerField(choices=GRATUITY_CHOICES, default=10)

    paid = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True)

    def __unicode__(self):
        return "{}'s appointment on {}, {}".format(self.user.get_full_name(), self.date, self.get_time_slot_display())

    def get_full_name(self):
        return "Appointment on {}, {}".format(self.date, self.get_time_slot_display())

    def get_price(self):
        total_price_before_tax = 0
        for serviced_car in self.servicedcar_set.all():
            for service in serviced_car.services.all():
                total_price_before_tax += service.fee

        return total_price_before_tax

    def is_first_paid_appt(self):
        return Appointment.objects.filter(user=self.user, paid=True).count() == 0

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    picture = models.ImageField(upload_to='service-pics', blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()

    def __unicode__(self):
        return "{0} (C${1})".format(self.name, self.fee)


class ServicedCar(models.Model):
    appointment = models.ForeignKey(Appointment)
    car = models.ForeignKey(Car)
    services = models.ManyToManyField(Service)
