from rest_framework.response import Response
from rest_framework.views import APIView

from pulseapi.profiles.models import ProfileType, ProgramType, ProgramYear


class UserProfileCategoriesView(APIView):
    def get(self, request, **kwargs):
        profile_types = list(ProfileType.objects.values_list('value', flat=True))
        program_types = list(ProgramType.objects.values_list('value', flat=True))
        program_years = list(ProgramYear.objects.values_list('value', flat=True))

        return Response({
            'profile_types': profile_types,
            'program_types': program_types,
            'program_years': program_years
        })
