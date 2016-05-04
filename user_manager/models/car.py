from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel


class Car(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    deleted = models.BooleanField(default=False)

    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField(validators=[
        MaxValueValidator(2050),
        MinValueValidator(1887)
    ])
    color = models.CharField(max_length=50)
    plate = models.CharField(max_length=15)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    ENGINE_TYPE = (
        ('3', 'V3'),
        ('4', 'V4'),
        ('5', 'V5'),
        ('6', 'V6'),
        ('8', 'V8'),
    )
    engine_type = models.CharField(choices=ENGINE_TYPE, default='4', max_length=2)

    additional_info = models.TextField(blank=True)

    def __unicode__(self):
        return "{0}'s {1} {2} {3}".format(self.owner.first_name, self.year, self.make, self.model)
