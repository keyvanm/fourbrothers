from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView
from appt_mgmt.forms import InvoiceForm
from appt_mgmt.models import Invoice
from appt_mgmt.views import get_appt_or_404
from fourbrothers.utils import LoginRequiredMixin
from user_manager.models.promo import Promotion, InvalidPromotionException
from django.conf import settings
from django.contrib import messages
import stripe
from user_manager.models.user_profile import CreditCard
from django.contrib.sites.shortcuts import get_current_site


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


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'appt_mgmt/appt-pay.html'

    def dispatch(self, request, *args, **kwargs):
        appt = self.get_appt()
        if appt.servicedcar_set.count() == 0:
            messages.warning(request, 'Your cart is empty. Please pick a car and one or more services for it')
            return redirect('appt-service', pk=appt.pk)
        return super(InvoiceCreateView, self).dispatch(request, *args, **kwargs)

    def get_appt(self):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        context['errors'] = []
        context['warnings'] = []
        appt = self.get_appt()
        context['appt'] = appt

        user_loyalty_points = self.request.user.profile.loyalty_points
        appt_fee = appt.get_price()
        if user_loyalty_points < 10 or appt_fee - 10 < 39.99:
            context['loyalty_choices'] = []
        elif user_loyalty_points < 20 or appt_fee - 20 < 39.99:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:2]
        elif user_loyalty_points < 30 or appt_fee - 30 < 39.99:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:3]
        elif user_loyalty_points < 40 or appt_fee - 40 < 39.99:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:4]
        elif user_loyalty_points < 50 or appt_fee - 50 < 39.99:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:5]
        else:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:6]

        invoice = self.get_invoice(appt, context)

        context['invoice'] = invoice
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['total_price_cents'] = invoice.total_price() * 100

        return context

    def get_invoice(self, appt, context):
        invoice = Invoice.create(appt)
        loyalty = self.request.GET.get('loyalty')
        promo = self.request.GET.get('promo')
        gratuity = self.request.GET.get('gratuity')
        if loyalty and promo:
            raise Http404
        if loyalty:
            try:
                loyalty = int(loyalty)
            except ValueError:
                raise Http404
            loyalty_choices = [choice[0] for choice in context['loyalty_choices']]
            if loyalty not in loyalty_choices:
                context['errors'].append('You cannot apply {0} loyalty points'.format(loyalty))
                invoice.loyalty = 0
            invoice.loyalty = loyalty
        if promo:
            try:
                invoice.promo = Promotion.get_promo(promo, appt)
            except InvalidPromotionException, e:
                context['warnings'].append(e.message)
        if gratuity:
            invoice.gratuity = int(gratuity)

        if invoice.fee_after_discount() < 39.99:
            context['errors'].append('You cannot order a cart under $39.99')
        return invoice

    def get_form(self, form_class=None):
        form = super(InvoiceCreateView, self).get_form(form_class=form_class)
        if self.request.method == 'GET':
            if self.request.GET.get('loyalty'):
                form.fields['loyalty'].initial = self.request.GET.get('loyalty')
            if self.request.GET.get('promo'):
                try:
                    promo = Promotion.get_promo(self.request.GET.get('promo'), self.get_appt())
                    form.fields['promo'].initial = promo
                except InvalidPromotionException:
                    pass
            if self.request.GET.get('gratuity'):
                gratuity = int(self.request.GET.get('gratuity'))
                if gratuity not in [choice[0] for choice in Invoice.GRATUITY_CHOICES]:
                    raise Http404
                form.fields['gratuity'].initial = self.request.GET.get('gratuity')

        return form

    def get_success_url(self):
        return reverse('appt-list')

    def form_valid(self, form):
        request = self.request
        form.instance.appointment = self.get_appt()
        form.instance.appt_fee = form.instance.appointment.get_price()

        user_loyalty_points = self.request.user.profile.loyalty_points
        if int(form.cleaned_data['loyalty']) > user_loyalty_points:
            raise ValidationError('You do not have enough loyalty points')

        total_payable = form.instance.total_price()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # stripe_public_key = settings.STRIPE_PUBLIC_KEY
        token = request.POST['stripeToken']
        try:
            if total_payable:
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

            self.request.user.profile.loyalty_points += int(total_payable / 20)
            self.request.user.profile.save()

            messages.success(request, 'Appointment booked successfully!')

        except stripe.CardError, e:
            # The card has been declined
            messages.warning(request, 'Transaction unsuccessful. Please try again.')
            return super(InvoiceCreateView, self).form_invalid(form)

        return super(InvoiceCreateView, self).form_valid(form)

