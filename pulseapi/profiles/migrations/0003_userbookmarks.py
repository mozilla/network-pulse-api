# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-04 18:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entries', '0013_entry_help_types'),
        ('profiles', '0002_auto_20170803_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBookmarks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarked_by_profile', to='entries.Entry')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmark_entries_from_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
