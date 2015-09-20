from django.conf.urls import *
from user_manager.views.car import CarCreateView, CarDetailView
from user_manager.views.profile import ProfileEditView, ProfileDetailView, ProfilePopulateView

urlpatterns = [
    url(r'^$', ProfileDetailView.as_view(), name='profile-detail'),
    url(r'^edit/$', ProfileEditView.as_view(), name='profile-edit'),
    url(r'^populate/$', ProfilePopulateView.as_view(), name='profile-populate'),

    url(r'^cars/create/$', CarCreateView.as_view(), name='car-create'),
    url(r'^cars/(?P<pk>\d+)/$', CarDetailView.as_view(), name='car-detail'),
]
