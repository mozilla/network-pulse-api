# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-19 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0011_remove_entry_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='ordered_creator_list',
            field=models.CharField(blank=True, max_length=9999),
        ),
    ]
