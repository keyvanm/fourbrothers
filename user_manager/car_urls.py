from django.conf.urls import url

from user_manager.views.car import CarListView, CarEditView, CarDeleteView, \
    CarCreateView

urlpatterns = [
    url(r'^$', CarListView.as_view(), name='car-list'),

    url(r'^add/$', CarCreateView.as_view(), name='car-add'),

    url(r'^(?P<pk>\d+)/edit/$', CarEditView.as_view(),
        name='car-edit'),

    url(r'^(?P<pk>\d+)/delete/$', CarDeleteView.as_view(),
        name='car-delete'),
]
