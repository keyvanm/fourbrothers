from django.conf.urls import *

# place app url patterns here
from appt_mgmt.views import ApptCreateView

urlpatterns = [
    url('^$', ApptCreateView.as_view(), name='appt-book'),
]
