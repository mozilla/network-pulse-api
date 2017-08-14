from django.db import migrations
from pulseapi.tags.helpers import remove_tags_with_commas

class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0003_collapse_case'),
    ]

    operations = [
        migrations.RunPython(remove_tags_with_commas),
    ]
