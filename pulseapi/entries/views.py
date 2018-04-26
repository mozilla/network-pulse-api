"""
Views to get entries
"""
import base64
import django_filters

from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q

from rest_framework import filters, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.entries.serializers import (
    EntrySerializerWithV1Creators,
    EntrySerializerWithCreators,
    ModerationStateSerializer,
)
from pulseapi.profiles.models import UserBookmarks

from pulseapi.utility.userpermissions import is_staff_address


@api_view(['PUT'])
def toggle_bookmark(request, entryid, **kwargs):
    """
    Toggle whether or not this user "bookmarked" the url-indicated entry.
    This is currently defined outside of the entry class, as functionality
    that is technically independent of entries themselves. We might
    change this in the future.
    """
    user = request.user

    if user.is_authenticated():
        entry = None
        profile = user.profile

        # find the entry for this id
        try:
            entry = Entry.objects.get(id=entryid)
        except Entry.DoesNotExist:
            return Response("No such entry", status=status.HTTP_404_NOT_FOUND)

        # find out if there is already a {user,entry,(timestamp)} triple
        bookmarks = entry.bookmarked_by.filter(profile=profile)
        exists = bookmarks.count() > 0

        # if there is a bookmark, remove it. Otherwise, make one.
        if exists:
            for bookmark in bookmarks:
                bookmark.delete()
        else:
            bookmark = UserBookmarks(entry=entry, profile=profile)
            bookmark.save()

        return Response("Toggled bookmark.", status=status.HTTP_204_NO_CONTENT)
    return Response("Anonymous bookmarks cannot be saved.", status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
def toggle_featured(request, entryid, **kwargs):
    """
    Toggle the featured status of an entry.
    """
    user = request.user

    if user.has_perm('entries.change_entry'):

        entry = None
        # find the entry for this id
        try:
            entry = Entry.objects.get(id=entryid)
        except Entry.DoesNotExist:
            return Response("No such entry", status=status.HTTP_404_NOT_FOUND)

        entry.featured = not entry.featured
        entry.save()
        return Response("Toggled featured status.",
                        status=status.HTTP_204_NO_CONTENT)
    return Response(
        "You donot have permission to change entry featured status.",
        status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
def toggle_moderation(request, entryid, stateid, **kwargs):
    """
    Toggle the moderation state for a specific entry,
    based on moderation state id values. These values
    can be obtained via /api/pulse/entries/moderation-states
    which returns id:name pairs for each available state.
    """
    user = request.user

    if user.has_perm('entries.change_entry') is True:
        entry = None
        moderation_state = None
        status404 = status.HTTP_404_NOT_FOUND

        # find the Entry in question
        try:
            entry = Entry.objects.get(id=entryid)
        except Entry.DoesNotExist:
            return Response("No such entry", status=status404)

        # find the ModerationState in question
        try:
            moderation_state = ModerationState.objects.get(id=stateid)
        except ModerationState.DoesNotExist:
            return Response("No such moderation state", status=status404)

        entry.moderation_state = moderation_state
        entry.save()

        status204 = status.HTTP_204_NO_CONTENT
        return Response("Updated moderation state.", status=status204)

    return Response(
        "You do not have permission to change entry moderation states.",
        status=status.HTTP_403_FORBIDDEN
    )


def post_validate(request):
    """
    Security helper function to ensure that a post request is session, CSRF, and nonce protected
    """
    user = request.user
    csrf_token = False
    nonce = False

    if request.data:
        csrf_token = request.data.get('csrfmiddlewaretoken', False)
        nonce = request.data.get('nonce', False)
    else:
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


class EntriesPagination(PageNumberPagination):
    """
    Add support for pagination and custom page size
    """
    # page size decided in https://github.com/mozilla/network-pulse-api/issues/39
    page_size = 48
    page_size_query_param = 'page_size'
    max_page_size = 1000


class EntryCustomFilter(filters.FilterSet):
    """
    We add custom filtering to allow you to filter by:
        * Tag - pass the `?tag=` query parameter
        * Issue - pass the `?issue=` query parameter
        * Help Type - pass the `?help_type=` query parameter
        * Featured - `?featured=True` (or False) - both capitalied
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
    help_type = django_filters.CharFilter(
        name='help_types__name',
        lookup_expr='iexact',
    )
    featured = django_filters.BooleanFilter(
        name='featured'
    )

    class Meta:
        """
        Required Meta class
        """
        model = Entry
        fields = ['tags', 'issues', 'featured', ]


class EntryView(RetrieveAPIView):
    """
    A view to retrieve individual entries
    """

    queryset = Entry.objects.public().with_related()
    pagination_class = None
    parser_classes = (
        JSONParser,
    )

    def get_serializer_class(self):
        request = self.request

        if request and request.version == settings.API_VERSIONS['version_1']:
            return EntrySerializerWithV1Creators

        return EntrySerializerWithCreators


class BookmarkedEntries(ListAPIView):
    pagination_class = EntriesPagination
    parser_classes = (
        JSONParser,
    )

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated() is False:
            return Entry.objects.none()

        bookmarks = UserBookmarks.objects.filter(profile=user.profile)
        return Entry.objects.filter(bookmarked_by__in=bookmarks).order_by('-bookmarked_by__timestamp')

    def get_serializer_class(self):
        request = self.request

        if request and request.version == settings.API_VERSIONS['version_1']:
            return EntrySerializerWithV1Creators

        return EntrySerializerWithCreators

    # When people POST to this route, we want to do some
    # custom validation involving CSRF and nonce validation,
    # so we intercept the POST handling a little.
    @detail_route(methods=['post'])
    def post(self, request, *args, **kwargs):
        validation_result = post_validate(request)

        if validation_result is True:
            # invalidate the nonce, so this form cannot be
            # resubmitted with the current id
            request.session['nonce'] = False

            user = request.user
            ids = self.request.query_params.get('ids', None)

            def bookmark_entry(id):
                entry = None

                # find the entry for this id
                try:
                    entry = Entry.objects.get(id=id)
                except:
                    return

                # find out if there is already a {user,entry,(timestamp)} triple
                profile = user.profile
                bookmarks = entry.bookmarked_by.filter(profile=profile)
                exists = bookmarks.count() > 0

                # make a bookmark if there isn't one already
                if exists is False:
                    bookmark = UserBookmarks(entry=entry, profile=profile)
                    bookmark.save()

            if ids is not None and user.is_authenticated():
                for id in ids.split(','):
                    bookmark_entry(id)

            return Response("Entries bookmarked.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                "post validation failed",
                status=status.HTTP_403_FORBIDDEN
            )


class ModerationStateView(ListAPIView):
    """
    A view to retrieve all moderation states
    """
    queryset = ModerationState.objects.all()
    serializer_class = ModerationStateSerializer
    parser_classes = (
        JSONParser,
    )


class EntriesListView(ListCreateAPIView):
    """
    A view that permits a GET to allow listing all the entries
    in the database

    **Route** - `/entries`

    #Query Parameters -

    - `?search=` - Search by title, description, get_involved, interest,
                   creator, and tag.
    - `?ids=` - Filter only for entries with specific ids. Argument
                must be a comma-separated list of integer ids.
    - `?tag=` - Allows filtering entries by a specific tag
    - `?issue=` - Allows filtering entries by a specific issue
    - `?help_type=` - Allows filtering entries by a specific help type
    - `?featured=True` (or False) - both capitalied. Boolean is set in admin UI
    - `?page=` - Page number, defaults to 1
    - `?page_size=` - Number of results on a page. Defaults to 48
    - `?ordering=` - Property you'd like to order the results by. Prepend with
                     `-` to reverse. e.g. `?ordering=-title`
    - `?moderationstate=` - Filter results to only show the indicated moderation
                            state, by name. This will only filter if the calling
                            user has moderation permissions.
    """
    pagination_class = EntriesPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filter_class = EntryCustomFilter
    search_fields = (
        'title',
        'description',
        'get_involved',
        'interest',
        'tags__name',
    )
    parser_classes = (
        JSONParser,
    )

    # Custom queryset handling: if the route was called as
    # /entries/?ids=1,2,3,4,... or /entries/?creators=a,b,c...
    # only return entries filtered on those property values.
    #
    # Otherwise, return all entries (with pagination).
    def get_queryset(self):
        user = self.request.user

        # Get all entries: if this is a normal call without a
        # specific moderation state, we return the set of
        # public entries. However, if moderation state is
        # explicitly requrested, and the requesting user has
        # permissions to change entries by virtue of being
        # either a moderator or superuser, we return all
        # entries, filtered for the indicated moderation state.
        queryset = False
        query_params = self.request.query_params
        modstate = query_params.get('moderationstate', None)

        if modstate is not None:
            is_superuser = user.is_superuser
            is_moderator = user.has_perm('entries.change_entry')

            if is_superuser is True or is_moderator is True:
                mvalue = ModerationState.objects.get(name=modstate)
                if mvalue is not None:
                    queryset = Entry.objects.filter(moderation_state=mvalue)

        if queryset is False:
            queryset = Entry.objects.public().with_related()

        # If the query was for a set of specific entries,
        # filter the query set further.
        ids = query_params.get('ids', None)

        if ids is not None:
            ids = [int(x) for x in ids.split(',')]
            queryset = queryset.filter(pk__in=ids)

        creators = query_params.get('creators', None)

        # If the query was for a set of entries by specifc creators,
        # filter the query set further.
        if creators is not None:
            creator_names = creators.split(',')

            # Filter only those entries by looking at their relationship
            # with creators (using the 'related_creators' field, which is
            # the OrderedCreatorRecord relation), and then getting each
            # relation's associated "creator" and making sure that the
            # creator's name is in the list of creator names specified
            # in the query string.
            #
            # This is achieved by Django by relying on namespace manging,
            # explained in the python documentation, specifically here:
            #
            # https://docs.python.org/3/tutorial/classes.html#private-variables-and-class-local-references

            queryset = queryset.filter(
                Q(related_entry_creators__profile__custom_name__in=creator_names) |
                Q(related_entry_creators__profile__related_user__name__in=creator_names)
            )

        return queryset

    def get_serializer_class(self):
        request = self.request

        if request and request.version == settings.API_VERSIONS['version_1']:
            return EntrySerializerWithV1Creators

        return EntrySerializerWithCreators

    # When people POST to this route, we want to do some
    # custom validation involving CSRF and nonce validation,
    # so we intercept the POST handling a little.
    @detail_route(methods=['post'])
    def post(self, request, *args, **kwargs):
        request_data = request.data
        user = request.user if hasattr(request, 'user') else None

        validation_result = post_validate(request)

        if validation_result is True:
            # invalidate the nonce, so this form cannot be
            # resubmitted with the current id
            request.session['nonce'] = False

            '''
            If there is a thumbnail, and it was sent as part of an
            application/json payload, then we need to unpack a thumbnail
            object payload and convert it to a Python ContentFile payload
            instead. We use a try/catch because the optional nature means
            we need to check using "if hasattr(request.data,'thumbnail'):"
            as we as "if request.data['thumnail']" and these are pretty
            much mutually exclusive patterns. A try/pass make far more sense.
            '''

            try:
                thumbnail = request_data['thumbnail']
                # do we actually need to repack as ContentFile?
                if thumbnail['name'] and thumbnail['base64']:
                    name = thumbnail['name']
                    encdata = thumbnail['base64']
                    proxy = ContentFile(base64.b64decode(encdata), name=name)
                    request_data['thumbnail'] = proxy
            except:
                pass

            # we also want to make sure that tags are properly split
            # on commas, in case we get e.g. ['a', 'b' 'c,d']
            if 'tags' in request_data:
                tags = request_data['tags']
                filtered_tags = []
                for tag in tags:
                    if ',' in tag:
                        filtered_tags = filtered_tags + tag.split(',')
                    else:
                        filtered_tags.append(tag)
                request_data['tags'] = filtered_tags

            serializer = self.get_serializer_class()(
                data=request_data,
                context={'user': user},
            )
            if serializer.is_valid():
                # ensure that the published_by is always the user doing
                # the posting, and set 'featured' to false.
                #
                # see https://github.com/mozilla/network-pulse-api/issues/83
                moderation_state = ModerationState.objects.get(
                    name='Pending'
                )

                if (is_staff_address(user.email)):
                    moderation_state = ModerationState.objects.get(
                        name='Approved'
                    )

                # save the entry
                saved_entry = serializer.save(
                    published_by=user,
                    featured=False,
                    moderation_state=moderation_state
                )

                return Response({'status': 'submitted', 'id': saved_entry.id})
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                "post validation failed - {}".format(validation_result),
                status=status.HTTP_400_BAD_REQUEST
            )
