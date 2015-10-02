# Create your views here.
from django.http.response import Http404

from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from appt_mgmt.models import Appointment
from fourbrothers.utils import LoginRequiredMixin, grouper


def get_appt_or_404(pk, user):
    appt = get_object_or_404(Appointment, pk=pk)
    # if (appt.user != user) or appt.deleted:
    #     raise Http404
    return appt


class ManagerScheduleListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/manager-schedule-list.html'

    def get_queryset(self):
        return Appointment.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ManagerScheduleListView, self).get_context_data(**kwargs)
        context['appts'] = grouper(self.object_list.all(), 3)
        return context


class ManagerScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'dashboard/manager-schedule-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_object_or_404(Appointment, pk=self.kwargs[self.pk_url_kwarg])


class TechScheduleListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/tech-schedule-list.html'

    def get_queryset(self):
        return self.request.user.assigned_appts

    def get_context_data(self, **kwargs):
        context = super(TechScheduleListView, self).get_context_data(**kwargs)
        # context['appts'] = grouper(self.object_list.all(), 3)
        return context


class TechScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'dashboard/tech-schedule-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_object_or_404(Appointment, pk=self.kwargs[self.pk_url_kwarg], technician=self.request.user)
