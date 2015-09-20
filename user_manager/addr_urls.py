from django.conf.urls import url

from user_manager.views.address import AddressListView, AddressEditView, AddressMakePrimaryView, AddressDeleteView, \
    AddressCreateView

urlpatterns = [
    url(r'^$', AddressListView.as_view(), name='address-list'),

    url(r'^add/$', AddressCreateView.as_view(), name='address-add'),

    url(r'^(?P<pk>\d+)/edit/$', AddressEditView.as_view(),
        name='address-edit'),

    url(r'^(?P<pk>\d+)/make-primary/$', AddressMakePrimaryView.as_view(),
        name='address-make-primary'),

    url(r'^(?P<pk>\d+)/delete/$', AddressDeleteView.as_view(),
        name='address-delete'),
]
