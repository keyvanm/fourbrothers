from django.conf.urls import *

# place app url patterns here
from dashboard.views import ManagerScheduleDetailView, ManagerScheduleListView, TechScheduleDetailView, \
    TechScheduleListView, ApptTechUpdate, ApptComplete

urlpatterns = [
    url(r'^manager/$', ManagerScheduleListView.as_view(), name='manager-schedule-list'),
    url(r'^manager/(?P<pk>\d+)/$', ManagerScheduleDetailView.as_view(), name='manager-schedule-detail'),
    url(r'^technician/$', TechScheduleListView.as_view(), name='tech-schedule-list'),
    url(r'^technician/(?P<pk>\d+)/$', TechScheduleDetailView.as_view(), name='tech-schedule-detail'),
    url(r'^technician/(?P<pk>\d+)/completed/$', ApptComplete.as_view(), name='appt-complete'),
    url(r'^technician/(?P<pk>\d+)/edit/technician/$', ApptTechUpdate.as_view(), name='appt-tech-edit'),
]
