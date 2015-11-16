import datetime

from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.utils import formats, six
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from appt_mgmt.models import Appointment, ServicedCar, Service
from fourbrothers.settings import MAX_NUM_APPT_TIME_SLOT
from user_manager.models.address import SharedParkingLocation


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
            if Appointment.objects.filter(date=date, time_slot=time_slot, paid=True).count() >= MAX_NUM_APPT_TIME_SLOT:
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


# class ServiceForm(ModelForm):
#     # date = forms.DateField(
#         # widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
#
#     class Meta:
#         model = ServicedCar
#         exclude = ['appointment']


class CarServiceForm(forms.ModelForm):
    class Meta:
        model = ServicedCar
        exclude = ['appointment']

    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.CheckboxSelectMultiple())

    # Overriding __init__ here allows us to provide initial
    # data for 'toppings' field
    # def __init__(self, *args, **kwargs):
    #     # Only in case we build the form from an instance
    #     # (otherwise, 'toppings' list should be empty)
    #     if 'instance' in kwargs:
    #         # We get the 'initial' keyword argument or initialize it
    #         # as a dict if it didn't exist.
    #         initial = kwargs.setdefault('initial', {})
    #         # The widget for a ModelMultipleChoiceField expects
    #         # a list of primary key for the selected data.
    #         initial['toppings'] = [t.pk for t in kwargs['instance'].topping_set.all()]
    #
    #     forms.ModelForm.__init__(self, *args, **kwargs)

    # Overriding save allows us to process the value of 'toppings' field
    # def save(self, commit=True):
    #     # Get the unsave Pizza instance
    #     instance = forms.ModelForm.save(self, False)
    #
    #     # Prepare a 'save_m2m' method for the form,
    #     old_save_m2m = self.save_m2m
    #
    #     def save_m2m():
    #         old_save_m2m()
    #         # This is where we actually link the pizza with toppings
    #         instance.service_set.clear()
    #         for service in self.cleaned_data['services']:
    #             instance.topping_set.add(service)
    #     self.save_m2m = save_m2m
    #
    #     # Do we need to save all changes now?
    #     if commit:
    #         instance.save()
    #         self.save_m2m()
    #
    #     return instance


class ApptTechForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['technician']

        # services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.CheckboxSelectMultiple())


class PayForm(forms.Form):
    LOYALTY_POINTS = (
        (0, '$0'),
        (10, '$10'),
        (20, '$20'),
        (30, '$30'),
        (40, '$40'),
        (50, '$50'),
    )

    gratuity = forms.ChoiceField(choices=Appointment.GRATUITY_CHOICES)
    promo_code = forms.CharField(required=False)
    loyalty = forms.ChoiceField(choices=LOYALTY_POINTS, required=False)


class InvalidDateException(ValidationError):
    pass
