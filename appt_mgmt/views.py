from datetime import date
import datetime

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http.response import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.views.generic.edit import CreateView, UpdateView, FormMixin

from django.contrib.humanize.templatetags.humanize import naturalday
import dateutil.parser

from appt_mgmt.forms import AppointmentForm, CarServiceForm, BuildingAppointmentForm, DateChoiceField, \
    InvalidDateException
from appt_mgmt.models import Appointment, ServicedCar
from fourbrothers.settings import MAX_NUM_APPT_TIME_SLOT
from fourbrothers.utils import LoginRequiredMixin, grouper
from user_manager.models.address import PrivateParkingLocation, SharedParkingLocation
from user_manager.models.car import Car


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    if (appt.user != user) or appt.canceled:
        raise Http404
    return appt


def count_appointment_for_date_and_time(requested_date, time_slot):
    qs = Appointment.objects.filter(date=requested_date, time_slot=time_slot)
    return len([appt for appt in qs if appt.paid])


class ApptCreateEditMixin(FormMixin):
    TIME_SLOT_CHOICES = Appointment.TIME_SLOT_CHOICES

    def time_slot_choices(self):
        if not self.request.GET.get('date'):
            return []

        requested_date = dateutil.parser.parse(self.request.GET.get('date')).date()
        _time_slot_choices = []

        today = requested_date.today()
        if requested_date >= today:
            pass
        elif requested_date == today:
            now = datetime.datetime.now()
            if now.hour < 7:
                pass
            elif now.hour < 10:
                self.TIME_SLOT_CHOICES = self.TIME_SLOT_CHOICES[1:]
            elif now.hour < 13:
                self.TIME_SLOT_CHOICES = self.TIME_SLOT_CHOICES[2:]
            elif now.hour < 16:
                self.TIME_SLOT_CHOICES = self.TIME_SLOT_CHOICES[3:]
            else:
                raise InvalidDateException('You cannot book an appointment on this date')
        elif requested_date < today:
            raise InvalidDateException('You cannot book an appointment on this date')

        for time_slot, time_slot_display in self.TIME_SLOT_CHOICES:
            if count_appointment_for_date_and_time(requested_date, time_slot) < MAX_NUM_APPT_TIME_SLOT:
                _time_slot_choices.append((time_slot, time_slot_display))

        return _time_slot_choices


class ApptCreateView(ApptCreateEditMixin, LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm

    def get_form(self, form_class=None):
        form = super(ApptCreateEditMixin, self).get_form(form_class)
        if self.request.GET.get('date'):
            date = dateutil.parser.parse(self.request.GET.get('date'))
            form.fields['date'].initial = date
            try:
                form.fields['time_slot'].choices = self.time_slot_choices()
            except InvalidDateException as e:
                form.errs = {'date': unicode(e.message)}

            if not form.fields['time_slot'].choices:
                form.errs = {'date': unicode(e.message)}
                form.fields['time_slot'].choices.append(("", "No more time slots left on this date"))
        else:
            form.fields['time_slot'].widget = forms.HiddenInput()
            form.fields['additional_info'].widget = forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super(ApptCreateEditMixin, self).get_context_data(**kwargs)
        context['date'] = self.request.GET.get('date')
        try:
            context['time_slot_choices'] = self.time_slot_choices()
        except InvalidDateException:
            context['time_slot_choices'] = []
        return context

    def get_success_url(self):
        return reverse('appt-service', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptCreateView, self).form_valid(form)


class PrivatePLApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/house-appt-create.html'

    def dispatch(self, request, *args, **kwargs):
        if PrivateParkingLocation.objects.filter(owner=self.request.user).exists():
            return super(PrivatePLApptCreateView, self).dispatch(request, *args, **kwargs)
        else:
            redirect_url = reverse('address-add-private')
            extra_params = '?next={}'.format(request.path)
            full_redirect_url = '{}{}'.format(redirect_url, extra_params)
            return HttpResponseRedirect(full_redirect_url)

    def get_form(self, form_class):
        form = super(PrivatePLApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = PrivateParkingLocation.objects.filter(owner=self.request.user)
        if not self.request.GET.get('date'):
            form.fields['address'].widget = forms.HiddenInput()
        return form


class SharedPLApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/building-appt-create.html'
    form_class = BuildingAppointmentForm

    def dispatch(self, request, *args, **kwargs):
        if SharedParkingLocation.objects.filter(owner=self.request.user).exists():
            return super(SharedPLApptCreateView, self).dispatch(request, *args, **kwargs)
        else:
            redirect_url = reverse('address-add-shared')
            extra_params = '?next={}'.format(request.path)
            full_redirect_url = '{}{}'.format(redirect_url, extra_params)
            return HttpResponseRedirect(full_redirect_url)

    def time_slot_choices(self):
        _time_slot_choices = super(SharedPLApptCreateView, self).time_slot_choices()
        if self.request.GET.get('building') and self.request.GET.get('date'):
            pl = get_object_or_404(SharedParkingLocation, pk=self.request.GET.get('building'))
            building = pl.building
            prescheduled_time_slots = [x['time_slot'] for x in
                                       building.available_slots.filter(date=self.request.GET.get('date')).values(
                                           'time_slot')]

            new_time_slot_choices = []
            for i, time_slot in enumerate(_time_slot_choices):
                if time_slot[0] in prescheduled_time_slots:
                    new_time_slot_choices.append(time_slot)
            return new_time_slot_choices
        return _time_slot_choices

    def get_form(self, form_class):
        form = super(SharedPLApptCreateView, self).get_form(form_class)
        form.fields['building'].queryset = SharedParkingLocation.objects.filter(owner=self.request.user)
        if self.request.GET.get('building'):
            pl = get_object_or_404(SharedParkingLocation, pk=self.request.GET.get('building'))
            form.fields['building'].initial = pl.id
            building = pl.building
            available_dates = list(set([x['date'] for x in building.available_slots.values('date')]))
            available_dates.sort()
            if available_dates:
                form.fields['date'] = DateChoiceField(
                    choices=[("", "-------------")] + zip(available_dates, map(naturalday, available_dates)))
                if self.request.GET.get('date'):
                    form.fields['date'].initial = self.request.GET.get('date')
            else:
                form.fields['date'] = forms.CharField(initial="There are no available dates for {}".format(building),
                                                      widget=forms.TextInput(attrs={'readonly': 'readonly'}))
        else:
            form.fields['date'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        pl = get_object_or_404(SharedParkingLocation, pk=self.request.GET.get('building'))
        form.instance.address = pl
        return super(SharedPLApptCreateView, self).form_valid(form)


class AppointmentEditView(ApptCreateEditMixin, LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appt_mgmt/appt-edit.html'
    # context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def get_form(self, form_class=None):
        form = super(ApptCreateEditMixin, self).get_form(form_class)
        try:
            self.object.address.privateparkinglocation
            form.fields['address'].queryset = PrivateParkingLocation.objects.filter(owner=self.request.user)
        except Exception as e:
            self.object.address.sharedparkinglocation
            form.fields['address'].queryset = SharedParkingLocation.objects.filter(owner=self.request.user)

        if self.request.GET.get('date'):
            date = dateutil.parser.parse(self.request.GET.get('date'))
            form.fields['date'].initial = date
            try:
                form.fields['time_slot'].choices = self.time_slot_choices()
            except InvalidDateException as e:
                form.errs = {'date': unicode(e.message)}

            if not form.fields['time_slot'].choices:
                form.errs = {'date': unicode(e.message)}
                form.fields['time_slot'].choices.append(("", "No more time slots left on this date"))
        else:
            form.fields['time_slot'].widget = forms.HiddenInput()
            form.fields['additional_info'].widget = forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super(ApptCreateEditMixin, self).get_context_data(**kwargs)
        context['date'] = self.request.GET.get('date')
        try:
            context['time_slot_choices'] = self.time_slot_choices()
        except InvalidDateException:
            context['time_slot_choices'] = []
        return context

    def get_success_url(self):
        appt = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        msg_plain = render_to_string('appt_mgmt/confirmation-email.txt', {'appt': appt})
        msg_html = render_to_string('appt_mgmt/confirmation-email.html', {'appt': appt})

        subject, from_email, to = 'Appointment Updated', 'info@fourbrothers.com', self.request.user.email
        if settings.SEND_MAIL:
            send_mail(
                subject,
                msg_plain,
                from_email,
                [to],
                html_message=msg_html,
                fail_silently=settings.DEBUG
            )
        return reverse('appt-list')


class ApptDelete(LoginRequiredMixin, DetailView):
    template_name = 'appt_mgmt/appt-delete.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)


class ApptDetailView(LoginRequiredMixin, DetailView):
    template_name = 'appt_mgmt/appt-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ApptDetailView, self).get_context_data(**kwargs)
        context['serviced_cars'] = ServicedCar.objects.filter(appointment=context['appt'])
        return context


class ApptListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appt_mgmt/appt-list.html'

    def get_queryset(self):
        return self.request.user.appointments

    def get_context_data(self, **kwargs):
        context = super(ApptListView, self).get_context_data(**kwargs)
        past_appointments = self.object_list.filter(date__lt=date.today(), invoice__isnull=False,
                                                    canceled=False).order_by('date')
        upcoming_appointments = self.object_list.filter(date__gte=date.today(), invoice__isnull=False,
                                                        canceled=False).order_by('date')
        # pending_appointments = self.object_list.filter(date__gte=date.today(), paid=False)

        context['past_appointments'] = grouper(past_appointments, 3)
        context['upcoming_appointments'] = grouper(upcoming_appointments, 3)
        # context['pending_appointments'] = grouper(pending_appointments, 3)
        return context


class ApptServiceCreateView(LoginRequiredMixin, CreateView):
    model = ServicedCar
    form_class = CarServiceForm
    template_name = 'appt_mgmt/appt-service.html'
    _cars = None
    _appt = None

    @property
    def appt(self):
        if not self._appt:
            self._appt = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        return self._appt

    @property
    def available_cars(self):
        if not self._cars:
            self._cars = Car.objects.filter(owner=self.request.user)
            #     .exclude(
            #     id__in=Car.objects.filter(servicedcar__appointment=self.appt)
            # )
        return self._cars

    def get_success_url(self):
        if '_addanother' in self.request.POST:
            return reverse('appt-service', kwargs={'pk': self.appt.pk})
        else:
            return reverse('appt-pay', kwargs={'pk': self.appt.pk})

    def dispatch(self, request, *args, **kwargs):
        if Car.objects.filter(owner=self.request.user).exists():
            return super(ApptServiceCreateView, self).dispatch(request, *args, **kwargs)
        else:
            redirect_url = reverse('car-add')
            extra_params = '?next={}'.format(request.path)
            full_redirect_url = '{}{}'.format(redirect_url, extra_params)
            return HttpResponseRedirect(full_redirect_url)

    def get_form(self, form_class=None):
        form = super(ApptServiceCreateView, self).get_form(form_class)
        form.fields['car'].queryset = self.available_cars
        return form

    def get_context_data(self, **kwargs):
        context = super(ApptServiceCreateView, self).get_context_data(**kwargs)
        context['available_cars'] = self.available_cars
        context['serviced_cars'] = ServicedCar.objects.filter(appointment=self.appt)
        context['total_so_far'] = self.appt.get_price()
        context['appt'] = self.appt
        return context

    def form_valid(self, form):
        form.instance.appointment = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptServiceCreateView, self).form_valid(form)

@csrf_exempt
@require_POST
def appt_service_delete_view(request, pk):
    serviced_car = get_object_or_404(ServicedCar, pk=pk)
    appt = serviced_car.appointment
    if appt.paid:
        return HttpResponse(status_code=404)
    serviced_car.delete()
    return HttpResponse()


class ApptCancelView(LoginRequiredMixin, View):
    def get(self, request, pk):
        appt = get_appt_or_404(pk, request.user)
        if appt.paid:
            return redirect('appt-list')
        if appt.servicedcar_set.count() == 0:
            appt.delete()
            return redirect('homepage')
        return redirect('appt-pay', pk=appt.pk)
