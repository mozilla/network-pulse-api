# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-07-25 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helptypes', '0001_initial'),
        ('entries', '0012_remove_entry_thumbnail_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='help_types',
            field=models.ManyToManyField(blank=True, related_name='entries', to='helptypes.HelpType'),
        ),
    ]