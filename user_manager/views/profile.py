from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from django.contrib import messages

from fourbrothers.utils import LoginRequiredMixin
from user_manager.forms import UserProfileForm
from user_manager.models.user_profile import UserProfile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'user_manager/profile/profile-edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form(self, form_class=None):
        form = super(ProfileEditView, self).get_form(self.get_form_class())
        form.initial.update({'first_name': self.request.user.first_name, 'last_name': self.request.user.last_name})
        return form

    def form_valid(self, form):
        form.instance.user.first_name = form.cleaned_data['first_name']
        form.instance.user.last_name = form.cleaned_data['last_name']
        form.instance.user.save()
        messages.success(self.request, 'Profile saved successfully')
        return super(ProfileEditView, self).form_valid(form)


class ProfilePopulateView(ProfileEditView):
    def get_success_url(self):
        return reverse('car-create')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_manager/profile/profile-detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile
