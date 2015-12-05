from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from appt_mgmt.forms import InvoiceForm
from appt_mgmt.models import Invoice
from appt_mgmt.views import get_appt_or_404
from fourbrothers.utils import LoginRequiredMixin
from user_manager.models.promo import Promotion
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
    template_name = 'appt_mgmt/appt-pay-2.html'

    def get_appt(self):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        context['errors'] = []
        appt = self.get_appt()
        context['appt'] = appt
        invoice = self.get_invoice(appt, context)

        context['invoice'] = invoice
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['total_price_cents'] = invoice.total_price() * 100

        user_loyalty_points = self.request.user.profile.loyalty_points
        appt_fee = invoice.appt_fee
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

        return context

    def get_invoice(self, appt, context):
        invoice = Invoice.create(appt)
        loyalty = self.request.GET.get('loyalty')
        promo = self.request.GET.get('promo')
        gratuity = self.request.GET.get('gratuity')
        if loyalty and promo:
            raise Http404
        if loyalty:
            invoice.loyalty = int(loyalty)
        if promo:
            try:
                invoice.promo = get_object_or_404(Promotion, code=promo)
            except Promotion.DoesNotExist:
                context['errors'].append('Invalid promotion code')
        if gratuity:
            invoice.gratuity = int(gratuity)

        if invoice.fee_after_discount < 39.99:
            context['errors'].append('You cannot order a cart under $39.99')
            invoice.loyalty = 0
            invoice.promo = None
        return invoice

    def get_form(self, form_class=None):
        form = super(InvoiceCreateView, self).get_form(form_class=form_class)
        if self.request.method == 'GET':
            if self.request.GET.get('loyalty'):
                form.fields['loyalty'].initial = self.request.GET.get('loyalty')
            if self.request.GET.get('promo'):
                form.fields['promo'].initial = self.request.GET.get('promo')
            if self.request.GET.get('gratuity'):
                form.fields['gratuity'].initial = self.request.GET.get('gratuity')

        return form

    def get_success_url(self):
        return reverse('appt-list')

    def form_valid(self, form):
        request = self.request
        form.instance.appt_fee = self.get_appt().get_price()
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

