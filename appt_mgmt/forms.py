from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.forms.models import ModelForm

from appt_mgmt.models import Appointment


class AppointmentForm(ModelForm):
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))

    class Meta:
        model = Appointment
        exclude = ['user', 'deleted', 'cars', 'technician']
