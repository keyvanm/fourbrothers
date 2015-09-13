from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from cinesend.utils import LoginRequiredMixin, grouper
from user_manager.forms import AddressForm
from user_manager.models.address import Address


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'user_manager/address_manager/address-list.html'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).exclude(privacy='public').order_by('-primary')

    def get_context_data(self, **kwargs):
        context = super(AddressListView, self).get_context_data(**kwargs)
        context['billing_addresses'] = grouper(self.object_list.filter(type='billing'), 3)
        context['shipping_addresses'] = grouper(self.object_list.filter(type='shipping'), 3)
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'user_manager/address_manager/address-create.html'

    def get_success_url(self):
        return reverse('address-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Address added successfully')
        return super(AddressCreateView, self).form_valid(form)


class ShippingAddressCreateView(AddressCreateView):
    def form_valid(self, form):
        form.instance.type = 'shipping'
        return super(ShippingAddressCreateView, self).form_valid(form)


class BillingAddressCreateView(AddressCreateView):
    def form_valid(self, form):
        form.instance.type = 'billing'
        return super(BillingAddressCreateView, self).form_valid(form)


class AddressEditView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'user_manager/address_manager/address-edit.html'

    def get_success_url(self):
        return reverse('address-list')

    def get_object(self, queryset=None):
        return get_object_or_404(Address, pk=self.kwargs[self.pk_url_kwarg], user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Address edited successfully')
        return super(AddressEditView, self).form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'user_manager/address_manager/address-delete.html'
    success_url = reverse_lazy('address-list')


class AddressMakePrimaryView(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user,
                                    primary=False)  # The address shouldn't already be the primary address

        # Unprimarify the previous primary address if it exists. If there are multiple primary addresses
        # (which should not happen), unprimarify all
        Address.objects.filter(user=request.user, primary=True, type=address.type).update(primary=False)

        address.primary = True
        address.save(update_fields=('primary',))
        messages.success(request, 'Primary {0} address changed'.format(address.type))
        return redirect('address-list')


class AddressDuplicateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.pk = None
        if address.type == 'shipping':
            address.type = 'billing'
        else:
            address.type = 'shipping'
        address.save()
        messages.success(request, 'Address successfully duplicated as a {0} address'.format(address.type))
        return redirect('address-list')