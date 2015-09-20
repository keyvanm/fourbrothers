from django.forms.models import ModelForm

from appt_mgmt.models import Appointment


class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        exclude = ['car', 'technician']
