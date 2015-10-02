from django.conf.urls import *

# place app url patterns here
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from appt_mgmt.views import BuildingApptCreateView, HouseApptCreateView, ApptDetailView, ApptListView

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='appt_mgmt/appt-choose-type.html')),
        name='appt-choose-type'),
    url(r'^building/$', BuildingApptCreateView.as_view(), name='appt-book-building'),
    url(r'^house/$', HouseApptCreateView.as_view(), name='appt-book-house'),
    url(r'^appointments/$', ApptListView.as_view(), name='appt-list'),
    url(r'^appointments/(?P<pk>\d+)/$', ApptDetailView.as_view(), name='appt-detail'),
]
