from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from fourbrothers.utils import LoginRequiredMixin, grouper  # , grouper
from user_manager.forms import SharedParkingLocationForm, PrivateAddressForm
from user_manager.models.address import Address, ParkingLocation, PrivateParkingLocation, SharedParkingLocation


class AddressListView(LoginRequiredMixin, ListView):
    model = ParkingLocation
    template_name = 'user_manager/address_manager/address-list.html'

    def get_queryset(self):
        return ParkingLocation.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AddressListView, self).get_context_data(**kwargs)
        context['addresses'] = grouper(self.object_list.all(), 3)
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = ParkingLocation
    template_name = 'user_manager/address_manager/address-create.html'
    redirect_field_name = 'next'

    def get_success_url(self):
        return self.request.POST.get(self.redirect_field_name) or reverse('address-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Address added successfully')
        return super(AddressCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddressCreateView, self).get_context_data(**kwargs)
        context['redirect_field_name'] = self.redirect_field_name
        context['redirect_field_value'] = self.request.GET.get(self.redirect_field_name)
        return context


class PrivateAddressCreateView(AddressCreateView):
    model = Address
    form_class = PrivateAddressForm

    def form_valid(self, form):
        response = super(PrivateAddressCreateView, self).form_valid(form)
        PrivateParkingLocation(name=form.cleaned_data['name'], address=form.instance, owner=self.request.user).save()
        return response


class SharedAddressCreateView(AddressCreateView):
    model = SharedParkingLocation
    form_class = SharedParkingLocationForm


class PrivateAddressEditView(LoginRequiredMixin, UpdateView):
    model = PrivateParkingLocation
    form_class = PrivateAddressForm
    template_name = 'user_manager/address_manager/address-edit.html'

    def get_success_url(self):
        return reverse('address-list')

    def form_valid(self, form):
        messages.success(self.request, 'Address edited successfully')
        return super(PrivateAddressEditView, self).form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = ParkingLocation
    template_name = 'user_manager/address_manager/address-delete.html'
    success_url = reverse_lazy('address-list')
