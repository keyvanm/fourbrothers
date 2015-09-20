from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from appt_mgmt.forms import AppointmentForm
from appt_mgmt.models import Appointment
from fourbrothers.utils import LoginRequiredMixin
from user_manager.models.address import Address


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    if (appt.user != user) or appt.deleted:
        raise Http404
    return appt


class ApptCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm

    def get_success_url(self):
        return reverse('appt-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Appointment booked successfully')
        return super(ApptCreateView, self).form_valid(form)


class HouseApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/house-appt-create.html'

    def get_form(self, form_class):
        form = super(HouseApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = Address.objects.filter(user=self.request.user, type='house')
        return form


class BuildingApptCreateView(ApptCreateView):
    template_name = 'appt_mgmt/building-appt-create.html'

    def get_form(self, form_class):
        form = super(BuildingApptCreateView, self).get_form(form_class)
        form.fields['address'].queryset = Address.objects.filter(user=self.request.user, type='building')
        return form



class ApptDetailView(LoginRequiredMixin, DetailView):
    template_name = 'appt_mgmt/appt-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_appt_or_404(self.kwargs[self.pk_url_kwarg], self.request.user)
