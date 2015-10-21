from datetime import date
from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context import Context
from django.template.loader import get_template, render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.humanize.templatetags.humanize import naturalday
import stripe
import dateutil.parser

from appt_mgmt.forms import AppointmentForm, CarServiceForm, BuildingAppointmentForm, DateChoiceField, \
    AppointmentEditForm, PayForm
from appt_mgmt.models import Appointment, ServicedCar
from fourbrothers.settings import MAX_NUM_APPT_TIME_SLOT
from fourbrothers.utils import LoginRequiredMixin, grouper
from user_manager.models.address import PrivateParkingLocation, SharedParkingLocation
from user_manager.models.car import Car
from user_manager.models.promo import Promotion, InvalidPromotionException
from user_manager.models.user_profile import CreditCard


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    if (appt.user != user) or appt.canceled:
        raise Http404
    return appt


class TermsView(LoginRequiredMixin, View):
    # template_name = "appt_mgmt/terms.html"
    # return render(request, 'appt_mgmt/terms.html')

    def get(self, request, pk):
        return render(request, template_name="appt_mgmt/terms.html", context={"pk":pk})

    # def get_success_url(self):
    #     return reverse('appt-pay', kwargs={'pk': self.appt.pk})


class ApptCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    TIME_SLOT_CHOICES = Appointment.TIME_SLOT_CHOICES

    def time_slot_choices(self):
        if not self.request.GET.get('date'):
            return []

        date = dateutil.parser.parse(self.request.GET.get('date'))
        _time_slot_choices = []
        for time_slot, time_slot_display in self.TIME_SLOT_CHOICES:
            if Appointment.objects.filter(date=date, time_slot=time_slot, paid=True).count() < MAX_NUM_APPT_TIME_SLOT:
                _time_slot_choices.append((time_slot, time_slot_display))

        return _time_slot_choices

    def get_success_url(self):
        return reverse('appt-service', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ApptCreateView, self).get_form(form_class)
        if self.request.GET.get('date'):
            date = dateutil.parser.parse(self.request.GET.get('date'))
            form.fields['date'].initial = date

            form.fields['time_slot'].choices = self.time_slot_choices()

            if not form.fields['time_slot'].choices:
                form.fields['time_slot'].choices.append(("", "No more time slots left on this date"))
        else:
            form.fields['time_slot'].widget = forms.HiddenInput()
            form.fields['additional_info'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ApptCreateView, self).get_context_data(**kwargs)
        context['date'] = self.request.GET.get('date')
        context['time_slot_choices'] = self.time_slot_choices()
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


class ApptEdit(UpdateView):
    model = Appointment
    form_class = AppointmentEditForm
    template_name = 'appt_mgmt/appt-edit.html'
    # context_object_name = 'appt'

    # def dispatch(self, *args, **kwargs):
    #     if not (
    #         self.request.user.appointments
    #     ):
    #         raise Http404

    def get_success_url(self):
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


class ApptListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appt_mgmt/appt-list.html'

    def get_queryset(self):
        return self.request.user.appointments

    def get_context_data(self, **kwargs):
        context = super(ApptListView, self).get_context_data(**kwargs)
        past_appointments = self.object_list.filter(date__lt=date.today(), paid=True).order_by('date')
        upcoming_appointments = self.object_list.filter(date__gte=date.today(), paid=True).order_by('date')
        # pending_appointments = self.object_list.filter(date__gte=date.today(), paid=False)

        context['past_appointments'] = grouper(past_appointments, 3)
        context['upcoming_appointments'] = grouper(upcoming_appointments, 3)
        # context['pending_appointments'] = grouper(pending_appointments, 3)
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

    def get_price(self, appt, sales_tax_percent, form, promo_code=None, loyalty=0):
        if promo_code:
            try:
                promotion = get_object_or_404(Promotion, code=promo_code)
                total_price_before_tax = promotion.get_discounted_price(appt)
            except InvalidPromotionException as e:
                total_price_before_tax = appt.get_price()
                form.add_error('promotion', e)
        else:
            total_price_before_tax = appt.get_price()

        if loyalty:
            if loyalty < self.request.user.profile.loyalty_points:
                total_price_before_tax -= loyalty
                self.request.user.profile.loyalty_points -= loyalty
            else:
                total_price_before_tax -= self.request.user.profile.loyalty_points
                self.request.user.profile.loyalty_points = 0

            self.request.user.profile.save()

        total_price_before_tax = total_price_before_tax.quantize(Decimal("1.00"))
        total_sales_tax = (total_price_before_tax * Decimal(sales_tax_percent / 100.0)).quantize(Decimal("1.00"))
        total_price = (total_price_before_tax + total_sales_tax).quantize(Decimal("1.00"))

        total_gratuity = (total_price * Decimal(appt.gratuity / 100.0)).quantize(Decimal("1.00"))
        total_price_after_gratuity = (total_price + total_gratuity).quantize(Decimal("1.00"))

        if total_price == 0:
            messages.warning(self.request, 'Your cart is empty')
            raise Http404
        return total_price_before_tax, total_sales_tax, total_price, total_gratuity, total_price_after_gratuity

    def get(self, request, pk):
        pay_form = PayForm(initial={'gratuity': '10'})
        user_loyalty_points = self.request.user.profile.loyalty_points
        if user_loyalty_points < 10:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:1]
        elif user_loyalty_points < 20:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:2]
        elif user_loyalty_points < 30:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:3]
        elif user_loyalty_points < 40:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:4]
        elif user_loyalty_points < 50:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:5]
        else:
            pay_form.fields['loyalty'].choices = pay_form.LOYALTY_POINTS[0:6]

        appt = get_appt_or_404(pk, request.user)

        if self.request.GET.get('loyalty'):
            loyalty = int(self.request.GET.get('loyalty'))
        else:
            loyalty = 0

        total_price_before_tax, total_sales_tax, total_price, total_gratuity, total_price_after_gratuity = self.get_price(
            appt, 13, form=pay_form, promo_code=self.request.GET.get('promo_code'), loyalty=loyalty)

        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        return render(request, 'appt_mgmt/appt-pay.html',
                      {'appt': appt, 'pay_form': pay_form, 'stripe_public_key': stripe_public_key,
                       'total_price_before_tax': total_price_before_tax, 'total_tax': total_sales_tax,
                       'total_price': total_price, 'total_gratuity': total_gratuity,
                       'total_price_after_gratuity': total_price_after_gratuity,
                       'total_price_cents': int(total_price_after_gratuity * 100)})

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        pay_form = PayForm(request.POST)
        if pay_form.is_valid():
            appt = get_appt_or_404(pk, request.user)
            appt.gratuity = int(pay_form.cleaned_data['gratuity'])
            appt.save()

            promo_code=pay_form.cleaned_data['promo_code']
            loyalty = pay_form.cleaned_data['loyalty']
            _, _, _, _, total_payable = self.get_price(appt, 13, form=pay_form, promo_code=promo_code, loyalty=loyalty)

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
                if promo_code:
                    try:
                        promotion = Promotion.objects.get(code=promo_code)
                        self.request.user.profile.promos_used.add(promotion)
                    except:
                        pass

                appt.paid = True
                appt.save(update_fields=('paid',))

                self.request.user.profile.loyalty_points += total_payable/20
                self.request.user.profile.save()

                messages.success(request, 'Appointment booked successfully!')

                msg_plain = render_to_string('appt_mgmt/email.txt', {'appt': appt})
                msg_html = render_to_string('appt_mgmt/email.html', {'appt': appt})

                subject, from_email, to = 'Appointment Confirmation', 'info@fourbrothers.com', self.request.user.email

                send_mail(
                    subject,
                    msg_plain,
                    from_email,
                    [to],
                    html_message=msg_html,
                    fail_silently=False
                )

                return redirect('appt-list')
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
            self._cars = Car.objects.filter(owner=self.request.user)
            #     .exclude(
            #     id__in=Car.objects.filter(servicedcar__appointment=self.appt)
            # )
        return self._cars

    def get_success_url(self):
        if '_addanother' in self.request.POST:
            return reverse('appt-service', kwargs={'pk': self.appt.pk})
        else:
            return reverse('appt-terms', kwargs={'pk': self.appt.pk})

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
        return context

    def form_valid(self, form):
        form.instance.appointment = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptServiceCreateView, self).form_valid(form)
