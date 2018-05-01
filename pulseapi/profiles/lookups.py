from ajax_select import register, LookupChannel
from django.db.models import Q
from itertools import chain

from pulseapi.profiles.models import UserProfile


@register('profiles')
class UserProfilesLookup(LookupChannel):
    model = UserProfile

    def get_query(self, q, request):
        queryset = self.model.objects.all()
        startswith_lookup = Q(custom_name__istartswith=q) | Q(related_user__name__istartswith=q)
        qs_startswith = queryset.filter(startswith_lookup)
        qs_contains = queryset.filter(
            Q(custom_name__icontains=q) | Q(related_user__name__icontains=q)
        ).exclude(startswith_lookup)

        return list(chain(qs_startswith, qs_contains))

    def format_item_display(self, item):
        return f'<span class="profile">{str(item)}</span>'

    def can_add(self, user, model):
        return user.has_perm('profiles.add_userprofile')
