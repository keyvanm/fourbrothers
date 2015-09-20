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

urlpatterns = [
    url(r'^accounts/address/', include('user_manager.addr_urls')),
    url(r'^accounts/cars/', include('user_manager.car_urls')),
    url(r'^accounts/profile/', include('user_manager.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='homepage'),
    url(r'^book/', include('appt_mgmt.urls')),
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
