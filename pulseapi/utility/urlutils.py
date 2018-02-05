from pulseapi.settings import VERSION_GROUP


def versioned_url(url_pattern=''):
    """
    Returns a url pattern with an optional version pattern included in it
    For e.g. r`^myurl/` will turn into `^myurl/<version pattern>/`
    where <version pattern> is the optional version regex pattern
    """
    return url_pattern + VERSION_GROUP


def api_url(url_pattern=''):
    """
    Returns a url pattern prefixed with the api namespace pattern which is `^api/pulse/`
    """
    return r'^api/pulse/' + url_pattern


def versioned_api_url(url_pattern=''):
    """
    Returns a url pattern prefixed with the api namespace pattern and
    the optional version pattern
    """
    return versioned_url(r'^api/pulse/') + url_pattern
