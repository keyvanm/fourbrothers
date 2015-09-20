from django.forms.models import ModelForm
from django import forms

from user_manager.models.address import Address
from user_manager.models.car import Car
from user_manager.models.user_profile import UserProfile


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'type', 'primary', ]


class UserProfileForm(ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', ]


class CarForm(ModelForm):
    class Meta:
        model = Car
        exclude = ['owner', 'deleted']
