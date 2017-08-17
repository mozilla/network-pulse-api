from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response
from rest_framework import filters, status

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import UserProfileSerializer


class ProfileView(RetrieveAPIView):
    """
    A view to retrieve individual profiles
    """

    def get_queryset(self):
        return UserProfile.objects.all()

    serializer_class = UserProfileSerializer
    pagination_class = None

	# When people POST to this route, we want to
	# update the profile with the new information.
    @detail_route(methods=['post'])
    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(id=self.kwargs['pk']);
        serializer = UserProfileSerializer(profile, data=request.data)

        if serializer.is_valid():
            profile = serializer.save()
            return Response({'status': 'updated', 'id': profile.id})

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
