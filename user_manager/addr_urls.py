from django.conf.urls import patterns, url

from user_manager.views.address import AddressListView, ShippingAddressCreateView, BillingAddressCreateView, \
    AddressEditView, AddressMakePrimaryView, AddressDeleteView, AddressDuplicateView


urlpatterns = patterns('asset_portal.views',
                       url(r'^$', AddressListView.as_view(), name='address-list'),

                       url(r'^add-shipping/$', ShippingAddressCreateView.as_view(), name='address-shipping-add'),
                       url(r'^add-billing/$', BillingAddressCreateView.as_view(), name='address-billing-add'),

                       url(r'^(?P<pk>\d+)/edit/$', AddressEditView.as_view(),
                           name='address-edit'),

                       url(r'^(?P<pk>\d+)/make-primary/$', AddressMakePrimaryView.as_view(),
                           name='address-make-primary'),

                       # url(r'^(?P<pk>\d+)/make-public/$', BillingAddressCreateView.as_view(),
                       #     name='address-make-public'),

                       url(r'^(?P<pk>\d+)/duplicate/$', AddressDuplicateView.as_view(),
                           name='address-duplicate'),

                       url(r'^(?P<pk>\d+)/delete/$', AddressDeleteView.as_view(),
                           name='address-delete'),
)