# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-05-08 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_auto_20190508_1743'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='profilerole',
            index=models.Index(fields=['profile', 'is_current', '_order'], name='uk_role_profile_current_order'),
        ),
        migrations.AddIndex(
            model_name='profilerole',
            index=models.Index(fields=['profile', 'is_current', 'profile_type'], name='uk_role_profile_current_type'),
        ),
        migrations.AddIndex(
            model_name='programmembershiprecord',
            index=models.Index(fields=['profile', '_order'], name='uk_membership_profile_order'),
        ),
    ]
