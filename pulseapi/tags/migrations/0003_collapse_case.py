from __future__ import unicode_literals

from django.db import migrations, models
from pulseapi.tags.helpers import lowercase_all

class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_meta_order'),
    ]

    operations = [
        migrations.RunPython(lowercase_all),
    ]
