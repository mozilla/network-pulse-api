from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from pulseapi.utility.userpermissions import is_staff_address


class PulseAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        name = data.get('name')
        user.name = ' '.join([
            data.get('first_name', ''),
            data.get('last_name', '')
        ]).strip() if not name else name

        if is_staff_address(user.email):
            user.is_staff = True

        return user

    def login(self, request, user):
        print('Here')
        return super().login(request, user)
