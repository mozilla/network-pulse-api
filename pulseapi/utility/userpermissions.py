from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

def is_staff_address(email):
    """
    This function determines whether a particular email address is a
    mozilla address or not. We strictly control mozilla.com and
    mozillafoundation.org addresses, and so filtering on the email
    domain section using exact string matching is acceptable.
    """
    if email is None:
        return False

    parts = email.split('@')
    domain = parts[1]

    if domain == 'mozilla.org':
        return True

    if domain == 'mozilla.com':
        return True

    if domain == 'mozillafoundation.org':
        return True

    return False


def add_user_to_main_site(user):
    """
    this does nothing outside of mezzanine
    """


def assign_group_policy(user, name):
    """
    add a specific group policy to a user's list of group policies.
    """
    try:
        group = Group.objects.get(name=name)
        group.user_set.add(user)
    except:
        print("group", name, "not found")


def set_user_permissions(backend, user, response, *args, **kwargs):
    """
    This is a social-auth pipeline function for automatically
    setting is_superuser permissions when a user logs in from a
    known-to-be mozilla account.
    """

    if user.email and is_staff_address(user.email) and user.is_staff is False:
        user.is_staff = True
        user.save()

        add_user_to_main_site(user)

        assign_group_policy(user, "staff")
