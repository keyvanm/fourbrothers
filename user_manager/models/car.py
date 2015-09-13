from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from user_manager.models.address import Address


class Car(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    address = models.ForeignKey(Address)

    def __unicode__(self):
        if self.user.first_name:
            name = self.user.first_name
        else:
            name = self.user.username

        return "{0}'s {1} {2}".format(name, self.make, self.model)
