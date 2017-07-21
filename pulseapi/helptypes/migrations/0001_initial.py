from __future__ import unicode_literals

from django.db import migrations, models
from pulseapi.helptypes.models import HelpType

def forwards_func(apps, schema_editor):
    HelpType.objects.get_or_create(
        name="Attend",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Create content",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Code",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Design",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Fundraise",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Join community",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Localize & translate",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Mentor",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Plan & organize",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Promote",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Take Action",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Test & feedback",
        description="Help us with ..."
    )
    HelpType.objects.get_or_create(
        name="Write documentation",
        description="Help us with ..."
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
