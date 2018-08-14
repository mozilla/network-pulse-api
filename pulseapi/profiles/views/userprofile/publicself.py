from rest_framework.generics import get_object_or_404

from .public import UserProfilePublicAPIView


class UserProfilePublicSelfAPIView(UserProfilePublicAPIView):
    def get_object(self):
        user = self.request.user
        return get_object_or_404(self.queryset, related_user=user)
