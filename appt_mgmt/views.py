from decimal import Decimal

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
import stripe

from appt_mgmt.forms import AppointmentForm, CarServiceForm
from appt_mgmt.models import Appointment, Service, ServicedCar
from fourbrothers.utils import LoginRequiredMixin, grouper
from user_manager.models.address import Address
from user_manager.models.user_profile import CreditCard


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    if (appt.user != user) or appt.deleted:
        raise Http404
    return appt


class ApptCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm

    def get_success_url(self):
        return reverse('appt-service', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptCreateView, self).form_valid(form)


class HouseApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/house-appt-create.html'

    def get_form(self, form_class):
        form = super(HouseApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = Address.objects.filter(user=self.request.user, building_type='house')
        return form


class BuildingApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/building-appt-create.html'

    def get_form(self, form_class):
        form = super(BuildingApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = Address.objects.filter(user=self.request.user, building_type='building')
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
    def get(self, request, pk):
        # jobs_to_pay_slug_list = request.GET.getlist("pay")
        # jobs_to_pay_list = get_jobs_to_pay_list(jobs_to_pay_slug_list, request.user)
        # total_price_before_tax = Decimal(0)
        # for job in jobs_to_pay_list:
        #     total_price_before_tax += job.fee
        #
        # if not jobs_to_pay_list or total_price_before_tax == 0:
        #     messages.warning(request, 'All items in your cart are already paid for.')
        #     raise Http404
        total_price_before_tax = 100
        total_price = (total_price_before_tax * Decimal("1.13")).quantize(Decimal("1.00"))
        total_tax = (total_price_before_tax * Decimal("0.13")).quantize(Decimal("1.00"))
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        return render(request, 'appt_mgmt/appt-pay.html',
                      {'total_price': total_price, 'stripe_public_key': stripe_public_key,
                       'total_price_before_tax': total_price_before_tax, 'total_tax': total_tax,
                       'total_price_cents': int(total_price * 100)})

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        total_price = 100
        total_price *= Decimal("1.13")

        if total_price == 0:
            messages.warning(request, 'All items in your cart are already paid for.')
            raise Http404
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        token = request.POST['stripeToken']
        try:
            if not request.user.profile.stripe_customer_id:
                create_and_charge_new_customer(request, token, total_price)
            else:
                customer = stripe.Customer.retrieve(request.user.profile.stripe_customer_id)
                if customer.get("deleted", None):
                    create_and_charge_new_customer(request, token, total_price)
                else:
                    token_object = stripe.Token.retrieve(token)
                    cc = get_or_none(CreditCard, user=request.user, fingerprint=token_object.card.fingerprint)
                    if cc is None:
                        card = customer.sources.create(source=token)
                        cc = CreditCard(user=request.user, fingerprint=card.fingerprint, card_id=card.id)
                        cc.save()
                    stripe.Charge.create(
                        amount=int(total_price * 100),  # amount in cents, again
                        currency="cad",
                        source=cc.card_id,
                        customer=customer.id,
                        description="Paid ${}".format(total_price)
                    )
            return redirect('appt-detail', pk=pk)
        except stripe.CardError, e:
            # The card has been declined
            messages.warning(request, 'Transaction unsuccessful. Please try again.')
            return redirect('appt-pay', pk=pk)


class ApptServiceCreateView(LoginRequiredMixin, CreateView):
    model = ServicedCar
    form_class = CarServiceForm
    template_name = 'appt_mgmt/appt-service.html'

    def get_success_url(self):
        return reverse('appt-pay', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.appointment = get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
        # messages.success(self.request, 'Appointment booked successfully')
        return super(ApptServiceCreateView, self).form_valid(form)

