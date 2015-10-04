from allauth.account.utils import get_next_redirect_url
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from fourbrothers.utils import LoginRequiredMixin, grouper
from user_manager.forms import CarForm
from user_manager.models.car import Car


def get_car_or_404(pk, user):
    car = get_object_or_404(Car, pk=pk)
    if (car.owner != user) or car.deleted:
        raise Http404
    return car


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'user_manager/car/car-create.html'
    redirect_field_name = 'next'

    def get_success_url(self):
        return self.request.POST.get(self.redirect_field_name) or reverse('car-list')


    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Car added successfully')
        return super(CarCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CarCreateView, self).get_context_data(**kwargs)
        context['redirect_field_name'] = self.redirect_field_name
        context['redirect_field_value'] = self.request.GET.get(self.redirect_field_name)
        return context


class FirstCarCreateView(CarCreateView):
    template_name = 'user_manager/car/car-create-first.html'

    def get_success_url(self):
        return reverse('appt-choose-type')


class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'user_manager/car/car-list.html'

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CarListView, self).get_context_data(**kwargs)
        context['cars'] = grouper(self.object_list.all(), 3)
        return context


class CarEditView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'user_manager/car/car-edit.html'

    def get_success_url(self):
        return reverse('car-list')

    def get_object(self, queryset=None):
        return get_car_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Car edited successfully')
        return super(CarEditView, self).form_valid(form)


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'user_manager/car/car-delete.html'
    success_url = reverse_lazy('car-list')
