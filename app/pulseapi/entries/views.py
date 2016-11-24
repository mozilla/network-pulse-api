"""
Views to get entries
"""

import django_filters
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
# from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

from pulseapi.entries.models import Entry
from pulseapi.entries.serializers import (
    EntrySerializer,
)


class EntryCustomFilter(filters.FilterSet):
    """
    We add custom filtering to allow you to filter by:
        * Tag - pass the `?tags=` query parameter
    Accepts only one filter value i.e. one tag and/or one
    category.
    """
    tags = django_filters.CharFilter(
        name='tags__name',
        lookup_expr='iexact',
    )

    class Meta:
        model = Entry
        fields = ['tags']

class  EntryView(RetrieveAPIView):
    """
    A view to retrieve individual entries
    """
    queryset = Entry.objects.public()
    serializer_class = EntrySerializer
    pagination_class = None

class EntriesListView(ListCreateAPIView):
    """
    This is copied from Science
    A view that permits a GET to allow listing all the projects
    in the database

    **Route** - `/entries`

    **Query Parameters** -

    - `?search=` - Allows search terms
    - `?sort=` - Allows sorting of entries.
        - date_created - `?sort=date_created`
        - date_updated - `?sort=date_updated`

        *To sort in descending order, prepend the field with a '-', for e.g.
        `?sort=-date_updated`*

    - `?tags=` - Allows filtering entries by a specific tag
    - `?categories=` - Allows filtering entries by a specific category
    - `?expand=` -
    Forces the response to include basic
    information about a relation instead of just
    hyperlinking the relation associated
    with this project.

           Currently supported values are `?expand=leads`,
           `?expand=events` and `?expand=leads,events`

    """
    queryset = Entry.objects.public()
    # pagination_class = PageNumberPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        # filters.OrderingFilter,
    )
    filter_class = EntryCustomFilter
    ordering_fields = (
        'date_created',
        'date_updated',
    )
    search_fields = (
        'title',
        'description',
    )
    serializer_class = EntrySerializer

    # def get_serializer_class(self):
    #     expand = self.request.query_params.get('expand')
    #     if expand is not None:
    #         expand = expand.split(',')
    #         if 'leads' in expand and 'events' not in expand:
    #             return ProjectLeadSerializer
    #         elif 'events' in expand and 'leads' not in expand:
    #             return ProjectEventSerializer
    #         elif 'events' in expand and 'leads' in expand:
    #             return ProjectExpandAllSerializer
    #         else:
    #             return EntrySerializer
    #     else:
    #         return EntrySerializer


# def serializer_class(self):
#     expand = self.request.query_params.get('expand')
#     if expand is not None:
#         expand = expand.split(',')
#         if 'users' in expand and 'events' not in expand:
#             return ProjectUserWithGithubSerializer
#         elif 'events' in expand and 'users' not in expand:
#             return ProjectEventWithGithubSerializer
#         elif 'events' in expand and 'users' in expand:
#             return ProjectExpandAllWithGithubSerializer
#         else:
#             return ProjectWithGithubSerializer
#     else:
#         return ProjectWithGithubSerializer





# class ProjectView(RetrieveAPIView):
#     """
#     A view that permits a GET to allow listing of a single project by providing
#     its `id` as a parameter

#     **Route** - `/projects/:id`

#     **Query Parameters** -

#     - `?expand=` -
#     Forces the response to include basic
#     information about a relation instead of just
#     hyperlinking the relation associated
#     with this project.

#            Currently supported values are `?expand=users`,
#            `?expand=events` and `?expand=users,events`

#     """
#     queryset = Project.objects.public()
#     get_serializer_class = serializer_class
#     pagination_class = None


# class ProjectSlugView(RetrieveAPIView):
#     """
#     A view that permits a GET to allow listing of a single project by providing
#     its `slug` as a parameter

#     **Route** - `/projects/:slug`

#     **Query Parameters** -

#     - `?expand=` -
#     Forces the response to include basic
#     information about a relation instead of just
#     hyperlinking the relation associated
#     with this project.

#            Currently supported values are `?expand=users`,
#            `?expand=events` and `?expand=users,events`
#     """

#     pagination_class = None
#     get_serializer_class = serializer_class
#     lookup_field = 'slug'

#     def get_queryset(self):
#         return Project.objects.public().slug(self.kwargs['slug'])


# class CategoryListView(ListAPIView):
#     """
#     A view that permits a GET to allow listing of all categories
#     in the database
#     """
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     pagination_class = None
