from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from model_utils.choices import Choices
from user_manager.models.promo import PromoCode


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile")
    stripe_customer_id = models.CharField(max_length=50, blank=True)

    TYPE_CHOICES = Choices('customer', 'technician')
    type = models.CharField(choices=TYPE_CHOICES, default=TYPE_CHOICES.customer, max_length=15)

    loyalty_points = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=20, blank=True)

    promos_used = models.ManyToManyField(PromoCode)

    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="invitees", blank=True, null=True)

    def __unicode__(self):
        return "%s's profile" % self.user.username


class CreditCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="creditcards")
    card_id = models.CharField(max_length=50)
    fingerprint = models.CharField(max_length=50)
    last_4_digits = models.CharField(max_length=4)


# automatically make a user profile when a user is created
def create_user_profile(sender, **kwargs):
    """When creating a new user, make a profile for him or her."""
    created = kwargs["created"]
    if created:
        u = kwargs["instance"]
        if not UserProfile.objects.filter(user=u):
            user_profile = UserProfile(user=u)
            user_profile.save()


post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
