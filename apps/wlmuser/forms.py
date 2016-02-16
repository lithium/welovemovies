from django import forms

from wlmuser.models import WlmUser


class ProfileForm(forms.ModelForm):
    class Meta:
        model = WlmUser
        fields = ('username', 'email')
