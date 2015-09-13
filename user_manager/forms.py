from django.forms.models import ModelForm
from user_manager.models.address import Address


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'type', 'privacy', 'primary', ]