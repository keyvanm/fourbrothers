from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from fourbrothers.utils import LoginRequiredMixin
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

    def get_success_url(self):
        return reverse('car-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Car added successfully')
        return super(CarCreateView, self).form_valid(form)


class CarDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_manager/car/car-detail.html'
    context_object_name = 'car'

    def get_object(self, queryset=None):
        return get_car_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
