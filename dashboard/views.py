# Create your views here.
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from appt_mgmt.forms import ApptTechForm
from appt_mgmt.models import Appointment
from fourbrothers.utils import LoginRequiredMixin, grouper, ManagerPermissionMixin, \
    ManagerTechnicianPermissionMixin


class ManagerScheduleListView(ManagerPermissionMixin, LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/manager-schedule-list.html'

    def get_queryset(self):
        return Appointment.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ManagerScheduleListView, self).get_context_data(**kwargs)
        context['appts'] = grouper(self.object_list.all(), 3)
        return context


class ManagerScheduleDetailView(ManagerPermissionMixin, LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'dashboard/manager-schedule-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_object_or_404(Appointment, pk=self.kwargs[self.pk_url_kwarg])


class TechScheduleListView(ManagerTechnicianPermissionMixin, LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/tech-schedule-list.html'

    def get_queryset(self):
        return Appointment.objects.filter(technician=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TechScheduleListView, self).get_context_data(**kwargs)
        context['appts'] = grouper(self.object_list.all(), 3)
        return context


class TechScheduleDetailView(ManagerTechnicianPermissionMixin, LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'dashboard/tech-schedule-detail.html'
    context_object_name = 'appt'

    def get_object(self, queryset=None):
        return get_object_or_404(Appointment, pk=self.kwargs[self.pk_url_kwarg])


class ApptTechUpdate(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = ApptTechForm
    template_name = 'appt_mgmt/appt-tech-update.html'

    def get_success_url(self):
        return reverse('manager-schedule-list')


class ApptComplete(LoginRequiredMixin, View):
    model=Appointment

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        appt = get_object_or_404(Appointment, pk=pk)

        msg_plain = render_to_string('appt_mgmt/completion-email.txt', {'appt': appt})
        msg_html = render_to_string('appt_mgmt/completion-email.html', {'appt': appt})

        subject, from_email, to = 'Appointment Completion', 'info@fourbrothers.com', self.request.user.email

        send_mail(
            subject,
            msg_plain,
            from_email,
            [to],
            html_message=msg_html,
            fail_silently=True
        )

        appt.completed = True
        appt.save()

        return redirect('tech-schedule-detail', pk=pk)

