# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic.edit import CreateView
from appt_mgmt.forms import AppointmentForm

from appt_mgmt.models import Appointment
from fourbrothers.utils import LoginRequiredMixin


class ApptCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appt_mgmt/appt-create.html'

    def get_success_url(self):
        return reverse('appt-detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        messages.success(self.request, 'Appointment booked successfully'.format(form.instance.film_title))
        return super(ApptCreateView, self).form_valid(form)
