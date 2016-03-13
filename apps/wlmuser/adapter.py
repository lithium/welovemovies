from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adapter
from django.core.urlresolvers import reverse

from wlmuser.models import WlmUser


class WlmSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return reverse('account_profile')

    def new_user(self, request, sociallogin):
        screen_name = sociallogin.account.extra_data.get('screen_name')
        try:
            existing_user = WlmUser.objects.get(twitter_screen_name=screen_name)
            return existing_user
        except WlmUser.DoesNotExist:
            return super(WlmSocialAccountAdapter, self).new_user(request, sociallogin)

    def save_user(self, request, sociallogin, form=None):
        u = sociallogin.user
        u.set_unusable_password()
        if form:
            get_account_adapter().save_user(request, u, form)
        else:
            if u.twitter_screen_name:
                # claim account
                if not u.username:
                    u.username = u.twitter_screen_name
                u.twitter_screen_name = None
                u.twitter_profile_image_url = None
                # u.save()
            else:
                get_account_adapter().populate_username(request, u)
        sociallogin.save(request)
        return u
