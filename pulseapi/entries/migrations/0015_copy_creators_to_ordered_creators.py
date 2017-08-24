from django.db import migrations
from pulseapi.entries.models import Entry
from pulseapi.creators.models import Creator, OrderedCreatorRecord


def migrate_creator_data(apps, schema_editor):
    """
    Rewrite the old "creator" information as relations
    dictated by the OrderedCreatorRecord object. While
    the original insertion order _is_ somewhere in the
    database, accessing it using an explicit link relation
    makes things much easier.
    """
    entries = apps.get_model('entries', 'Entry').objects.all()
    for entry in entries:
        modern_entry = Entry.objects.get(id=entry.id)

        for creator in entry.creators.all():
            link = OrderedCreatorRecord.objects.create(
                entry=modern_entry,
                creator=Creator.objects.get(id=creator.id)
            );


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0014_entry_orderedcreators'),
    ]

    operations = [
        migrations.RunPython(migrate_creator_data),
    ]
