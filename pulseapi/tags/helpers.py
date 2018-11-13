import re

from pulseapi.entries.models import Entry
from pulseapi.tags.models import Tag


def collapse_case():
    """
    This function collapses all tags with multiple instances
    that differe in case to "the first tag", rebinding all
    entries that might have used one of the duplicates so
    that they point to the only tag that is left by this
    weeding procedure.
    """

    all_tags = Tag.objects.all()
    duplicates = []
    for master in all_tags:

        # Skip over any tags that we already encountered earlier during
        # duplication checking. We do this check in a case insensitive way
        # by comparing lowercase strings.
        # Note that this only works for languages that are well-behaved
        # when it comes to case lowering, such as English.
        if master.name.lower() in duplicates:
            continue

        # find any duplicates for this tag
        tag_set = Tag.objects.filter(name__iexact=master.name).exclude(name=master.name)

        if len(tag_set) > 0:
            # iterate over all tag duplicates
            for dupe in tag_set:
                # find all entries that use this duplicate, and effect a
                # "swap" of duplicate/master by first adding the master
                # tag, and then once we've updated all entries that use
                # the duplicate, deleting that duplicate.
                for entry in Entry.objects.filter(tags__name=dupe.name):
                    entry.tags.add(master)

                # Record that we processed this tag, in a way that allows
                # for a case insensitive check. Again, note that this only
                # works for languages that are well behaved when it comes
                # to case lowering (such as English)
                lname = dupe.name.lower()
                if (lname in duplicates) is False:
                    duplicates.append(lname)

                dupe.delete()


def lowercase_all(app, schema_editor):
    """
    This function converts all tags to lowercase.

    This can only be done if there are no duplicate
    instances of a tag with differing case, and so
    before the lowercase conversion this function will
    call collapse_case() to ensure a valid state as
    precondition.
    """

    # enforce precondition
    collapse_case()

    # force all tags to lowercase
    for tag in Tag.objects.all():
        tag.name = tag.name.lower()
        tag.save()


def remove_tags_with_commas(app, schema_editor):
    """
    This function analyses any tag for whether it contains
    commas. If it does, it splits on comma, trims the result,
    and then either creates a new tag, or uses an existing tag,
    to retag any entry that had a comma-encumbered tag (or tags).
    """

    tags_with_commas = Tag.objects.filter(name__contains=',')

    for tag in tags_with_commas:
        # Get all entries that use this tag right now, because
        # we're going to need to change what it points to.
        entries = Entry.objects.filter(tags__name=tag.name)

        # Create a list of plain string "tags" that we get by
        # resolving the comma(s) in our comma-laden tag.
        trimmed = tag.name.strip()
        splitlist = re.split(r'\s*,\s*', trimmed)
        filtered = list(filter(None, splitlist))

        # For each tag string we now have, update the entries that
        # used this tag so that they're tagged with the right thing
        # instead of our comma-encumbered tag.
        for tag_string in filtered:
            (retag, created) = Tag.objects.get_or_create(name=tag_string)
            for entry in entries:
                if retag in entry.tags.all():
                    continue
                else:
                    entry.tags.add(retag)

        # After updating all entries to use the new (set of) tag(s),
        # we can safely delete this offending comma-encumbered tag.
        tag.delete()
