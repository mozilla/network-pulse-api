# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 21:13
from __future__ import unicode_literals

from django.db import migrations, models
from pulseapi.issues.models import Issue

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    # issue = apps.get_model("issues", "Issue")
    Issue.objects.get_or_create(
        name="Web Literacy",
        description="People have the skills to read, write and participate in the digital world. Together, these informed digital citizens move beyond just consuming content — to creating, shaping and defending the web."
    )
    Issue.objects.get_or_create(
        name="Online Privacy & Security",
        description="People understand and can meaningfully control how their data is collected and used online — and trust that it’s safe. Companies and governments work to protect our data and enhance our ownership over our digital identities."
    )
    Issue.objects.get_or_create(
        name="Digital Inclusion",
        description="People everywhere can access and have the opportunity to participate in building the entire internet. Everyone on the internet has the opportunity to access and shape our digital world. The internet reflects the diversity of the people who use it."
    )
    Issue.objects.get_or_create(
        name="Decentralization",
        description="The technologies and platforms people use every day are interoperable and based on open standards. People expect and demand systems that allow seamless flow and transfer of information and content."
    )

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=300)),
            ],
        ),
        migrations.RunPython(forwards_func),
    ]
