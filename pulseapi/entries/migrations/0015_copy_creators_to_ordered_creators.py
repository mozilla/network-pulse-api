from django.db import migrations


def migrate_creator_data(apps, schema_editor):
    """
    Rewrite the old "creator" information as relations
    dictated by the OrderedCreatorRecord object. While
    the original insertion order _is_ somewhere in the
    database, accessing it using an explicit link relation
    makes things much easier.
    """
    Entry = apps.get_model('entries', 'Entry')
    OrderedCreatorRecord = apps.get_model('creators', 'OrderedCreatorRecord')
    entries = Entry.objects.all()
    for entry in entries:
        for creator in entry.creators.all():
            OrderedCreatorRecord.objects.create(
                entry=entry,
                creator=creator,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0014_entry_orderedcreators'),
    ]

    operations = [
        migrations.RunPython(migrate_creator_data),
    ]
