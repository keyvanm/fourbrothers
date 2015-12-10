from django.forms.models import ModelForm
from django import forms

from user_manager.models.address import Address, SharedParkingLocation, PrivateParkingLocation
from user_manager.models.car import Car
from user_manager.models.user_profile import UserProfile


class PrivateAddressForm(ModelForm):
    # name = forms.CharField(label='Address Nickname')

    class Meta:
        model = Address
        fields = ('address1', 'address2', 'city', 'state', 'postal_code', 'country')


class SharedParkingLocationForm(ModelForm):
    class Meta:
        model = SharedParkingLocation
        fields = ('building',)


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


class MySignupForm(forms.Form):
    first_name = forms.CharField(max_length=40, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=40, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = forms.CharField(max_length=40, required=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Phone number'}))
    newsletter_subscription = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked': 'true'}), required=False)

    def signup(self, request, user):
        form = MySignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.phone_number = form.cleaned_data['phone_number']
            user.profile.newsletter = form.cleaned_data['newsletter_subscription']
            user.profile.save()
            user.save()
