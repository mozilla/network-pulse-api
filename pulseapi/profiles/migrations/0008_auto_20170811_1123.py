# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-11 18:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import pulseapi.profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0001_initial'),
        ('profiles', '0007_auto_20170804_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=500, null=True)),
                ('country', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SocialUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('service', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='userbookmarks',
            options={'verbose_name': 'Bookmarks', 'verbose_name_plural': 'Bookmarks'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'Profile'},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='custom_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_group',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='issues',
            field=models.ManyToManyField(to='issues.Issue'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='thumbnail',
            field=models.ImageField(blank=True, max_length=2048, upload_to=pulseapi.profiles.models.entry_thumbnail_path),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_bio',
            field=models.CharField(blank=True, default='', max_length=140),
        ),
        migrations.AddField(
            model_name='socialurl',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.UserProfile'),
        ),
        migrations.AddField(
            model_name='location',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.UserProfile'),
        ),
    ]
