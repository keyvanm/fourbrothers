import datetime

from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.forms.models import ModelForm

from appt_mgmt.models import Appointment, ServicedCar, Service


class AppointmentForm(ModelForm):
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False,
                                       "startDate": str(datetime.date.today())}))

    class Meta:
        model = Appointment
        exclude = ['user', 'deleted', 'cars', 'technician', 'paid']

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("You can't pick a date in the past!")
        return date

    def clean(self):
        cleaned_data = super(AppointmentForm, self).clean()
        date = cleaned_data['date']
        time_slot = cleaned_data['time_slot']

        if Appointment.objects.filter(date=date, time_slot=time_slot).count() > 10:
            raise forms.ValidationError("Can't book more than 10 appointments in one time slot")


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
