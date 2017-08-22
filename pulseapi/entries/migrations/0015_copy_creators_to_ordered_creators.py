from django.db import migrations
from pulseapi.entries.models import Entry
from pulseapi.creators.models import OrderedCreatorRecord


def migrate_creator_data(apps, schema_editor):
    entries = Entry.objects.all()
    for entry in entries:
      for creator in entry.creators.all():
        print (entry.title, ' <=> ', creator.name);
        link = OrderedCreatorRecord.objects.create(
          entry=entry,
          creator=creator
        );


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0014_entry_orderedcreators'),
    ]

    operations = [
        migrations.RunPython(migrate_creator_data),
    ]
