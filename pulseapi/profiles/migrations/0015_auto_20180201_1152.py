# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-02-01 19:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_bootstrap_relations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiletype',
            name='value',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='programtype',
            name='value',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='programyear',
            name='value',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileType'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='program_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.ProgramType'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='program_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.ProgramYear'),
        ),
    ]
