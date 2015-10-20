"""fourbrothers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import update_session_auth_hash
from django.views.generic.base import TemplateView
import appt_mgmt
from fourbrothers.views import index_view

urlpatterns = [
    url(r'^accounts/address/', include('user_manager.addr_urls')),
    url(r'^accounts/cars/', include('user_manager.car_urls')),
    url(r'^accounts/profile/', include('user_manager.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', index_view, name='homepage'),
    url(r'^book/', include('appt_mgmt.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^about/', TemplateView.as_view(template_name='static-content/about.html'), name='about'),
    url(r'^services/', TemplateView.as_view(template_name='static-content/services.html'), name='services'),
    url(r'^faq/', TemplateView.as_view(template_name='static-content/faq.html'), name='faq'),
    url(r'^contact/', TemplateView.as_view(template_name='static-content/contact.html'), name='contact'),
    url(r'^careers/', TemplateView.as_view(template_name='static-content/careers.html'), name='careers'),
    url(r'^terms/', TemplateView.as_view(template_name='static-content/terms.html'), name='terms'),
    url(r'^corporate/', TemplateView.as_view(template_name='static-content/corporate.html'), name='corporate'),
    url(r'^privacy-statement/', TemplateView.as_view(template_name='static-content/privacy.html'), name='privacy-statement'),
    url(r'^report-error/', TemplateView.as_view(template_name='static-content/report.html'), name='report-error'),
    url(r'^help/', TemplateView.as_view(template_name='static-content/help.html'), name='help'),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = TemplateView.as_view(template_name="500.html")


# To prevent logging users out upon password change
def update_session_hash_signal_receiver(sender, **kwargs):
    user = kwargs["user"]
    request = kwargs["request"]
    update_session_auth_hash(request, user)


    # password_changed.connect(update_session_hash_signal_receiver)
    # password_set.connect(update_session_hash_signal_receiver)
    # password_reset.connect(update_session_hash_signal_receiver)
