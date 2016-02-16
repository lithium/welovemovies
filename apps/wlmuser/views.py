from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView

from wlmuser.forms import ProfileForm
from wlmuser.models import WlmUser


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'user/profile.html'
    form_class = ProfileForm
    model = WlmUser
    success_url = reverse_lazy('account_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile saved.")
        return super(ProfileView, self).form_valid(form)


