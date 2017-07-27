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
        # skip over any tags we already processed as duplicate earlier
        if master.name.lower() in duplicates:
            continue

        # find any duplicates for this tag
        tag_set = Tag.objects.filter(name__iexact=master.name).exclude(name=master.name)

        if len(tag_set) > 0:
            # iterate over all tag duplicates
            for dupe in tag_set:
                # find all entries that use this duplicate
                for entry in Entry.objects.filter(tags__name=dupe.name):
                    # replace duplicate tag with master tag
                    entry.tags.add(master)
                # record that we processed this tag, then delete it
                duplicates.append(dupe)
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
