from django.db import models
from django.db.models.signals import post_save
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile")
    # stripe_customer_id = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return "%s's profile" % self.user.username


# class CreditCard(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="creditcards")
#     card_id = models.CharField(max_length=50)
#     fingerprint = models.CharField(max_length=50)


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
