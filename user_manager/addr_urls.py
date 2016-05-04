from django.conf.urls import url

from user_manager.views.address import AddressListView, PrivateAddressEditView, AddressDeleteView, \
    PrivateAddressCreateView, SharedAddressCreateView

urlpatterns = [
    url(r'^$', AddressListView.as_view(), name='address-list'),

    # url(r'^add/$', AddressCreateView.as_view(), name='address-add'),
    url(r'^add-private/$', PrivateAddressCreateView.as_view(), name='address-add-private'),
    url(r'^add-public/$', SharedAddressCreateView.as_view(), name='address-add-shared'),

    url(r'^(?P<pk>\d+)/edit/$', PrivateAddressEditView.as_view(),
        name='address-edit'),

    url(r'^(?P<pk>\d+)/delete/$', AddressDeleteView.as_view(),
        name='address-delete'),
]
