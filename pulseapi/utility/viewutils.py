from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """
    Add support for pagination and custom page size
    """
    # page size decided in https://github.com/mozilla/network-pulse-api/issues/39
    page_size = 48
    page_size_query_param = 'page_size'
    max_page_size = 1000
