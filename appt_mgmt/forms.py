import datetime

from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.utils import formats, six
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from appt_mgmt.models import Appointment, ServicedCar, Service, Invoice
from fourbrothers.settings import MAX_NUM_APPT_TIME_SLOT
from user_manager.models.address import SharedParkingLocation
from user_manager.models.promo import Promotion


class DateChoiceField(forms.ChoiceField):
    input_formats = formats.get_format_lazy('DATE_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid date.'),
    }

    def to_python(self, value):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value

        unicode_value = force_text(value, strings_only=True)
        if isinstance(unicode_value, six.text_type):
            value = unicode_value.strip()
        # If unicode, try to strptime against each input format.
        if isinstance(value, six.text_type):
            for format in self.input_formats:
                try:
                    return self.strptime(value, format)
                except (ValueError, TypeError):
                    continue
        raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

    def strptime(self, value, format):
        return datetime.datetime.strptime(force_str(value), format).date()


# def tomorrow():
#     return datetime.date.today() + datetime.timedelta(days=1)
#
#
# def valid_start_date_for_booking_appointments():
#     now = datetime.datetime.now()
#     nov_11th = dateutil.parser.parse('2015-11-10').date()
#     if now.date() < nov_11th:
#         return nov_11th
#     if now.hour > 16:
#         return tomorrow()
#     else:
#         return now.date()


class AppointmentForm(ModelForm):
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False,
                                       # "startDate": str(valid_start_date_for_booking_appointments())
                                       }))

    class Meta:
        model = Appointment
        fields = ['date', 'address', 'time_slot', 'additional_info']

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("You can't pick a date in the past!")
        return date

    def clean(self):
        cleaned_data = super(AppointmentForm, self).clean()
        date = cleaned_data.get('date')
        today = date.today()
        if (date == today and datetime.datetime.now()) or date < today:
            raise InvalidDateException('You cannot book an appointment on this date')
        if date:
            time_slot = cleaned_data['time_slot']
            if Appointment.objects.filter(date=date, time_slot=time_slot).count() >= MAX_NUM_APPT_TIME_SLOT:
                raise InvalidDateException("Can't book more than 10 appointments in one time slot")


# class AppointmentEditForm(ModelForm):
#     date = forms.DateField(
#         widget=DateTimePicker(options={
#                                   "format": "YYYY-MM-DD",
#                                   "pickTime": False,
#                                   # "startDate": str(valid_start_date_for_booking_appointments())
#                               }))
#
#     class Meta:
#         model = Appointment
#         fields = ['date', 'time_slot', 'address']
#
#     def clean_date(self):
#         date = self.cleaned_data['date']
#         if date < datetime.date.today():
#             raise forms.ValidationError("You can't pick a date in the past!")
#         return date
#
#     def clean(self):
#         cleaned_data = super(AppointmentEditForm, self).clean()
#         date = cleaned_data.get('date')
#         if date:
#             time_slot = cleaned_data['time_slot']
#             if Appointment.objects.filter(date=date, time_slot=time_slot, paid=True).count() >= MAX_NUM_APPT_TIME_SLOT:
#                 raise forms.ValidationError("Can't book more than 10 appointments in one time slot")


class BuildingAppointmentForm(AppointmentForm):
    building = forms.ModelChoiceField(SharedParkingLocation.objects.all())

    class Meta:
        model = Appointment
        fields = ['building', 'date', 'time_slot']


class CarServiceForm(forms.ModelForm):
    class Meta:
        model = ServicedCar
        exclude = ['appointment']

    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.CheckboxSelectMultiple())


class ApptTechForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['technician']


class InvoiceForm(forms.ModelForm):
    gratuity = forms.ChoiceField(choices=Invoice.GRATUITY_CHOICES, initial=10)
    promo = forms.ModelChoiceField(required=False, queryset=Promotion.objects.all(), widget=forms.HiddenInput())
    loyalty = forms.ChoiceField(choices=Invoice.LOYALTY_CHOICES, widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Invoice
        fields = ['gratuity', 'promo', 'loyalty']


class InvalidDateException(ValidationError):
    pass
