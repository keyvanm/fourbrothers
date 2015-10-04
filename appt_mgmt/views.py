from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.views.generic.edit import CreateView, UpdateView
import stripe
import dateutil.parser

from appt_mgmt.forms import AppointmentForm, CarServiceForm
from appt_mgmt.models import Appointment, ServicedCar
from fourbrothers.settings import MAX_NUM_APPT_TIME_SLOT
from fourbrothers.utils import LoginRequiredMixin, grouper
from user_manager.models.address import PrivateParkingLocation, SharedParkingLocation
from user_manager.models.car import Car
from user_manager.models.user_profile import CreditCard


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    if (appt.user != user) or appt.deleted:
        raise Http404
    return appt


class ApptCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    TIME_SLOT_CHOICES = Appointment.TIME_SLOT_CHOICES
    _time_slot_choices = []

    @property
    def time_slot_choices(self):
        self._time_slot_choices = []
        if not self.request.GET.get('date'):
            return self._time_slot_choices

        date = dateutil.parser.parse(self.request.GET.get('date'))
        for time_slot, time_slot_display in self.TIME_SLOT_CHOICES:
            if Appointment.objects.filter(date=date, time_slot=time_slot, paid=True).count() < MAX_NUM_APPT_TIME_SLOT:
                self._time_slot_choices.append((time_slot, time_slot_display))

        return self._time_slot_choices

    def get_success_url(self):
        return reverse('appt-service', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ApptCreateView, self).get_form(form_class)
        if self.request.GET.get('date'):
            date = dateutil.parser.parse(self.request.GET.get('date'))
            form.fields['date'].initial = date

            form.fields['time_slot'].choices = self.time_slot_choices

            if not self.time_slot_choices:
                form.fields['time_slot'].choices.append(("", "No more time slots left on this date"))
        else:
            form.fields['time_slot'].widget = forms.HiddenInput()
            form.fields['address'].widget = forms.HiddenInput()
            form.fields['gratuity'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ApptCreateView, self).get_context_data(**kwargs)
        context['date'] = self.request.GET.get('date')
        context['time_slot_choices'] = self.time_slot_choices
        return context


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
        return form


class SharedPLApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/building-appt-create.html'

    def dispatch(self, request, *args, **kwargs):
        if SharedParkingLocation.objects.filter(owner=self.request.user).exists():
            return super(SharedPLApptCreateView, self).dispatch(request, *args, **kwargs)
        else:
            redirect_url = reverse('address-add-shared')
            extra_params = '?next={}'.format(request.path)
            full_redirect_url = '{}{}'.format(redirect_url, extra_params)
            return HttpResponseRedirect(full_redirect_url)

    def get_form(self, form_class):
        form = super(SharedPLApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = SharedParkingLocation.objects.filter(owner=self.request.user)
        return form


class ApptDetailView(LoginRequiredMixin, DetailView):
    template_name = 'appt_mgmt/appt-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)


class ApptListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appt_mgmt/appt-list.html'

    def get_queryset(self):
        return self.request.user.appointments

    def get_context_data(self, **kwargs):
        context = super(ApptListView, self).get_context_data(**kwargs)
        context['appts'] = grouper(self.object_list.all(), 3)
        return context


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def create_and_charge_new_customer(request, token, total_price):
    request.user.creditcards.all().delete()
    customer = stripe.Customer.create(
        source=token,
        description="{}, customer of {}".format(request.user.get_full_name(),
                                                get_current_site(request).name),
        email=request.user.email
    )
    request.user.profile.stripe_customer_id = customer.stripe_id
    request.user.profile.save()
    stripe.Charge.create(
        amount=int(total_price * 100),  # amount in cents, again
        currency="cad",
        customer=customer.id,
        description="Paid ${} for service".format(total_price)
    )


class ApptPayView(LoginRequiredMixin, View):
    def get_price(self, appt, sales_tax_percent):
        total_price_before_tax = 0
        for serviced_car in appt.servicedcar_set.all():
            for service in serviced_car.services.all():
                total_price_before_tax += service.fee

        total_price_before_tax = total_price_before_tax.quantize(Decimal("1.00"))
        total_sales_tax = (total_price_before_tax * Decimal(sales_tax_percent / 100.0)).quantize(Decimal("1.00"))
        total_price = (total_price_before_tax + total_sales_tax).quantize(Decimal("1.00"))
        total_price_after_gratuity = total_price * Decimal(1 + appt.gratuity / 100.0)

        if total_price == 0:
            messages.warning(self.request, 'Your cart is empty')
            raise Http404
        return total_price_before_tax, total_sales_tax, total_price, total_price_after_gratuity

    def get(self, request, pk):
        appt = get_appt_or_404(pk, request.user)
        total_price_before_tax, total_sales_tax, total_price, total_price_after_gratuity = self.get_price(appt, 13)

        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        return render(request, 'appt_mgmt/appt-pay.html',
                      {'appt': appt, 'stripe_public_key': stripe_public_key,
                       'total_price_before_tax': total_price_before_tax, 'total_tax': total_sales_tax,
                       'total_price': total_price, 'total_price_after_gratuity': total_price_after_gratuity,
                       'total_price_cents': int(total_price * 100)})

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        appt = get_appt_or_404(pk, request.user)

        _, _, _, total_payable = self.get_price(appt, 13)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        # stripe_public_key = settings.STRIPE_PUBLIC_KEY
        token = request.POST['stripeToken']
        try:
            if not request.user.profile.stripe_customer_id:
                create_and_charge_new_customer(request, token, total_payable)
            else:
                customer = stripe.Customer.retrieve(request.user.profile.stripe_customer_id)
                if customer.get("deleted", None):
                    create_and_charge_new_customer(request, token, total_payable)
                else:
                    token_object = stripe.Token.retrieve(token)
                    cc = get_or_none(CreditCard, user=request.user, fingerprint=token_object.card.fingerprint)
                    if cc is None:
                        card = customer.sources.create(source=token)
                        cc = CreditCard(user=request.user, fingerprint=card.fingerprint, card_id=card.id)
                        cc.save()
                    stripe.Charge.create(
                        amount=int(total_payable * 100),  # amount in cents, again
                        currency="cad",
                        source=cc.card_id,
                        customer=customer.id,
                        description="Paid ${}".format(total_payable)
                    )
            appt.paid = True
            appt.save(update_fields=('paid',))

            messages.success(request, 'Appointment booked successfully!')
            return redirect('appt-detail', pk=pk)
        except stripe.CardError, e:
            # The card has been declined
            messages.warning(request, 'Transaction unsuccessful. Please try again.')
            return redirect('appt-pay', pk=pk)


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
            self._cars = Car.objects.filter(owner=self.request.user).exclude(
                id__in=Car.objects.filter(servicedcar__appointment=self.appt)
            )
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

    def get_form(self, form_class):
        form = super(ApptServiceCreateView, self).get_form(form_class)
        form.fields['car'].queryset = self.available_cars
        return form

    def get_context_data(self, **kwargs):
        context = super(ApptServiceCreateView, self).get_context_data(**kwargs)
        context['available_cars'] = self.available_cars
        return context

    def form_valid(self, form):
        form.instance.appointment = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptServiceCreateView, self).form_valid(form)


