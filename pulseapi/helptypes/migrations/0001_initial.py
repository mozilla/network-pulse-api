from __future__ import unicode_literals

from django.db import migrations, models
from pulseapi.issues.models import HelpType

def forwards_func(apps, schema_editor):
    HelpType.objects.get_or_create(
        name="Help design",
        description="..."
    )
    HelpType.objects.get_or_create(
        name="Help program",
        description="..."
    )
    HelpType.objects.get_or_create(
        name="Help spread the word",
        description="..."
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HelpType',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
        migrations.RunPython(forwards_func),
    ]
