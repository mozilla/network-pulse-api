def is_moz(email):
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

    if domain == 'mozilla.com':
        return True

    if domain == 'mozillafoundation.org':
        return True

    if domain == 'mozilla.org':
        return True

    return False
