from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from django_extensions.db.models import TimeStampedModel

from user_manager.models.address import Address, ParkingLocation
from user_manager.models.car import Car
from user_manager.models.promo import Promotion


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

    @property
    def paid(self):
        try:
            return self.invoice is not None
        except:
            return False

    completed = models.BooleanField(default=False)
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
        qs = Appointment.objects.filter(user=self.user)
        return len([appt for appt in qs if appt.paid]) == 0


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


def decimalize(func):
    def func_wrapper(*args, **kwargs):
        return func(*args, **kwargs).quantize(Decimal("1.00"))

    return func_wrapper


class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment)

    appt_fee = models.DecimalField(max_digits=10, decimal_places=2)

    GRATUITY_CHOICES = (
        (0, '0%'),
        (5, '5%'),
        (10, '10%'),
        (15, '15%'),
        (20, '20%'),
    )
    gratuity = models.PositiveSmallIntegerField(choices=GRATUITY_CHOICES, default=10)

    LOYALTY_CHOICES = (
        (0, '$0'),
        (10, '$10'),
        (20, '$20'),
        (30, '$30'),
        (40, '$40'),
        (50, '$50'),
    )
    loyalty = models.PositiveSmallIntegerField(choices=LOYALTY_CHOICES, default=0)

    promo = models.ForeignKey(Promotion, blank=True, null=True)

    @classmethod
    def create(cls, appointment):
        invoice = cls(appointment=appointment)
        invoice.appt_fee = appointment.get_price()
        return invoice

    def discount_type(self):
        if self.loyalty and self.promo:
            raise DoubleDiscountException('You cannot use loyalty points and promotion code in one cart')
        if self.loyalty:
            return "loyalty"
        if self.promo:
            return "promo"
        return None

    def pretty_discount_type(self):
        discount = self.discount_type()
        if discount == "loyalty":
            return "Loyalty Points"
        if discount == "promo":
            return "Promo code ({0})".format(self.promo)

    @decimalize
    def discount(self):
        if self.discount_type() == "loyalty":
            return Decimal(self.loyalty)
        if self.discount_type() == "promo":
            return self.promo.get_discount_on_appt(self.appointment)
        return Decimal(0)

    @decimalize
    def fee_after_discount(self):
        return Decimal(self.appt_fee) - self.discount()

    @decimalize
    def gratuity_amount(self):
        return self.fee_after_discount() * Decimal(self.gratuity / 100.0)

    @decimalize
    def tax(self):
        return self.fee_after_discount() * Decimal(0.13)

    @decimalize
    def fee_after_tax(self):
        return self.fee_after_discount() * Decimal(1.13)

    @decimalize
    def total_price(self):
        return self.fee_after_tax() + self.gratuity_amount()

    def clean(self):
        if self.fee_after_discount < 39.99:
            raise ValidationError('You cannot order a cart under $39.99')

    def save(self, *args, **kwargs):
        if self.promo:
            self.appointment.user.profile.promos_used.add(self.promo)
        if self.loyalty:
            self.appointment.user.profile.loyalty_points -= self.loyalty
            self.appointment.user.profile.save()

        msg_plain = render_to_string('appt_mgmt/confirmation-email.txt', {'appt': self.appointment})
        msg_html = render_to_string('appt_mgmt/confirmation-email.html', {'appt': self.appointment})

        subject, from_email, to = 'Appointment Confirmation', 'info@fourbrothers.com', self.appointment.user.email

        if settings.SEND_MAIL:
            send_mail(
                subject,
                msg_plain,
                from_email,
                [to],
                html_message=msg_html,
                fail_silently=settings.DEBUG
            )
        return super(Invoice, self).save(*args, **kwargs)


class DoubleDiscountException(ValidationError):
    pass
