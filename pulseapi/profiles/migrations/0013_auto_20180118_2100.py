# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-01-18 21:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_remove_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='affiliation',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_extended_information',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='program_type',
            field=models.CharField(choices=[('None', 'None'), ('Mozilla Fellow', 'Mozilla Fellow')], default='None', max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='program_year',
            field=models.CharField(choices=[('----', '----'), ('2005', '2005'), ('2006', '2006'), ('2007', '2007'), ('2008', '2008'), ('2009', '2009'), ('2010', '2010'), ('2011', '2011'), ('2012', '2012'), ('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019')], default='----', max_length=4),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_bio_long',
            field=models.CharField(blank=True, max_length=4096),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_bio',
            field=models.CharField(blank=True, max_length=212),
        ),
    ]
