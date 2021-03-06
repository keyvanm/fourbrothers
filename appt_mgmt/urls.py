from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from appt_mgmt.invoice_views import InvoiceCreateView

from appt_mgmt.views import SharedPLApptCreateView, PrivatePLApptCreateView, ApptDetailView, ApptListView, \
    ApptServiceCreateView, AppointmentEditView, ApptDelete, appt_service_delete_view, ApptCancelView


urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='appt_mgmt/appt-choose-type.html'),
                              login_url="/accounts/signup/"),
        name='appt-choose-type'),
    # url(r'^terms/$', terms_view, name='terms'),
    url(r'^building/$', SharedPLApptCreateView.as_view(), name='appt-book-building'),
    url(r'^building/$', SharedPLApptCreateView.as_view(), name='appt-book-building'),
    url(r'^house/$', PrivatePLApptCreateView.as_view(), name='appt-book-house'),
    # url(r'(?P<pk>\d+)/pay/$', ApptPayView.as_view(), name='appt-pay'),
    url(r'(?P<pk>\d+)/pay/$', InvoiceCreateView.as_view(), name='appt-pay'),
    url(r'^appointments/$', ApptListView.as_view(), name='appt-list'),
    url(r'^appointments/(?P<pk>\d+)/edit/$', AppointmentEditView.as_view(), name='appt-edit'),
    url(r'^appointments/(?P<pk>\d+)/delete/$', ApptDelete.as_view(), name='appt-delete'),
    url(r'^appointments/(?P<pk>\d+)/$', ApptDetailView.as_view(), name='appt-detail'),
    url(r'^appointments/(?P<pk>\d+)/add-service/$', ApptServiceCreateView.as_view(), name='appt-service'),
    url(r'^servicedcar/(?P<pk>\d+)/delete/$', appt_service_delete_view, name='appt-service-delete'),

    url(r'^appointments/(?P<pk>\d+)/cancel/$', ApptCancelView.as_view(), name='appt-cancel'),

]
