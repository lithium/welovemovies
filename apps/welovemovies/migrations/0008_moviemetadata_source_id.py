# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-14 20:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welovemovies', '0007_viewing_how_watched'),
    ]

    operations = [
        migrations.AddField(
            model_name='moviemetadata',
            name='source_id',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
