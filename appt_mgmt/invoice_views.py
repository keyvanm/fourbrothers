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
    """Retreive an object of type model from the database based on the
    arguments. Return None if no such object exists."""
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def create_and_charge_new_customer(request, token, total_price):
    """Create a new customer object on Stripe, and charge them the amount of
    total_price"""

    # We want to create a new customer on Stripe delete all the credit card info
    # this user has on our database since they will be invalid
    request.user.creditcards.all().delete()
    customer = stripe.Customer.create(
        source=token,
        description="{}, customer of {}".format(request.user.get_full_name(),
                                                get_current_site(request).name),
        email=request.user.email
    )
    # If the website is being run in demo mode, do not associate the stripe id
    # to the user
    if not settings.DEBUG:
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
        """This method gets called first when this view is invoked"""
        appt = self.get_appt()
        # If the user hasn't selected any cars, send them back to select one.
        if appt.servicedcar_set.count() == 0:
            messages.warning(request, 'Your cart is empty. Please pick a car and one or more services for it')
            return redirect('appt-service', pk=appt.pk)
        return super(InvoiceCreateView, self).dispatch(request, *args, **kwargs)

    def get_appt(self):
        # Get an appointment object, if it doesn't exist serve a 404 page
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def get_context_data(self, **kwargs):
        """This method populates the view with calculated data (context)"""
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        context['errors'] = []
        context['warnings'] = []
        appt = self.get_appt()
        context['appt'] = appt

        user_loyalty_points = self.request.user.profile.loyalty_points
        appt_fee = appt.get_price()
        # Do not show the loyalty points option that exceed the amount of their
        # cart
        if user_loyalty_points < 10 or appt_fee - 10 < 39.98:
            context['loyalty_choices'] = []
        elif user_loyalty_points < 20 or appt_fee - 20 < 39.98:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:2]
        elif user_loyalty_points < 30 or appt_fee - 30 < 39.98:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:3]
        elif user_loyalty_points < 40 or appt_fee - 40 < 39.98:
            context['loyalty_choices'] = Invoice.LOYALTY_CHOICES[0:4]
        elif user_loyalty_points < 50 or appt_fee - 50 < 39.98:
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
            # Cannot use both a promo code and loyalty points
            raise Http404
        if loyalty:
            # make sure the amount of loyalty used is valid
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
            # Make sure the promo used, exists, and is valid
            try:
                invoice.promo = Promotion.get_promo(promo, appt)
            except InvalidPromotionException, e:
                context['warnings'].append(e.message)
        if gratuity:
            invoice.gratuity = int(gratuity)

        if invoice.fee_after_discount() < 39.98:
            context['errors'].append('You cannot order a cart under $39.99')
        return invoice

    def get_form(self, form_class=None):
        """Prepopulates form fields based on GET query parameters"""
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
        """Redirect to the list of appointments if payment is successful"""
        return reverse('appt-list')

    def form_valid(self, form):
        """This method is called by django if the form passes
        all validation (form is valid)"""

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
                    # A first time customer doesn't have a stripe id asscoiated yet
                    create_and_charge_new_customer(request, token, total_payable)
                else:
                    # retrieve the customer from stripe API
                    customer = stripe.Customer.retrieve(request.user.profile.stripe_customer_id)
                    if customer.get("deleted", None):
                        create_and_charge_new_customer(request, token, total_payable)
                    else:
                        token_object = stripe.Token.retrieve(token)
                        # Checking if the user has a credit card saved or not
                        cc = get_or_none(CreditCard, user=request.user, fingerprint=token_object.card.fingerprint)
                        if cc is None:
                            # Create a new credit card object if one does not exist
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
            # Add loyalty points to user based on their purchase amount
            self.request.user.profile.loyalty_points += int(total_payable / 20)
            self.request.user.profile.save()

            messages.success(request, 'Appointment booked successfully!')

        except stripe.CardError, e:
            # The card has been declined
            messages.warning(request, 'Transaction unsuccessful. Please try again.')
            # If the card was declined, call form_invalid and let django
            # redirect the user back to payment page
            return super(InvoiceCreateView, self).form_invalid(form)

        return super(InvoiceCreateView, self).form_valid(form)
