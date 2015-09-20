from django.conf.urls import *
from user_manager.views.profile import ProfileEditView, ProfileDetailView

urlpatterns = [
    url(r'^$', ProfileDetailView.as_view(), name='profile-detail'),
    url(r'^edit/$', ProfileEditView.as_view(), name='profile-edit'),
]
