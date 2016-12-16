"""
Views to get entries
"""

import django_filters
from rest_framework import (filters, status)
from rest_framework.decorators import detail_route
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from pulseapi.entries.models import Entry
from pulseapi.entries.serializers import EntrySerializer

def post_validate(request):
    """
    Security helper function to ensure that a post request is session, CSRF, and nonce protected
    """

    user = request.user
    csrf_token = request.POST.get('csrfmiddlewaretoken', False)
    nonce = request.POST.get('nonce', False)

    # ignore post attempts without a CSRF token
    if csrf_token is False:
        return "No CSRF token in POST data."

    # ignore post attempts without a known form id
    if nonce is False:
        return "No form identifier in POST data."

    # ignore post attempts by clients that are not logged in
    if not user.is_authenticated:
        return "Anonymous posting is not supported."

    # ignore unexpected post attempts (i.e. missing the session-based unique form id)
    if nonce != request.session['nonce']:
        # invalidate the nonce entirely, so people can't retry until there's an id collision
        request.session['nonce'] = False
        return "Forms cannot be auto-resubmitted (e.g. by reloading)."

    return True


class EntryCustomFilter(filters.FilterSet):
    """
    We add custom filtering to allow you to filter by:
        * Tag - pass the `?tag=` query parameter
        * Issue - pass the `?issue=` query parameter
    Accepts only one filter value i.e. one tag and/or one
    category.
    """
    tag = django_filters.CharFilter(
        name='tags__name',
        lookup_expr='iexact',
    )
    issue = django_filters.CharFilter(
        name='issues__name',
        lookup_expr='iexact',
    )

    class Meta:
        """
        Required Meta class
        """
        model = Entry
        fields = ['tags', 'issues',]


class EntryView(RetrieveAPIView):
    """
    A view to retrieve individual entries
    """
    queryset = Entry.objects.public()
    serializer_class = EntrySerializer
    pagination_class = None


class EntriesListView(ListCreateAPIView):
    """
    A view that permits a GET to allow listing all the entries
    in the database

    **Route** - `/entries`

    **Query Parameters** -

    - `?search=` - Allows search terms
    - `?tag=` - Allows filtering entries by a specific tag
    - `?issue=` - Allows filtering entries by a specific issue
    """
    queryset = Entry.objects.public()
    pagination_class = PageNumberPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
    )
    filter_class = EntryCustomFilter
    search_fields = (
        'title',
        'description',
    )
    serializer_class = EntrySerializer

    # When people POST to this route, we want to do some
    # custom validation involving CSRF and nonce validation,
    # so we intercept the POST handling a little.
    @detail_route(methods=['post'])
    def post(self, request, *args, **kwargs):
        validation_result = post_validate(request)

        if validation_result is True:
            # invalidate the nonce, so this form cannot be resubmitted with the current id
            request.session['nonce'] = False

            serializer = EntrySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'submitted'})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("post validation failed", status=status.HTTP_400_BAD_REQUEST)
