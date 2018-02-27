"""
Create fake tags for local development and Heroku's review app.
"""

from factory import DjangoModelFactory, Faker

from pulseapi.tags.models import Tag

tags = [
    'community',
    'curriculum',
    'digital inclusion',
    'education',
    'fake news',
    'global sprint',
    'iot',
    'libraries',
    'mozfest',
    'online privacy & security',
    'open data',
    'open science',
    'open source',
    'science',
    'web literacy',
    'working open'
]


class TagFactory(DjangoModelFactory):

    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = Faker('word', ext_word_list=tags)
