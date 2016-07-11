# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-13 06:12
from __future__ import unicode_literals

from django.db import migrations, models
import mainsite.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedSite',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(mainsite.models.StatsMixin, 'sites.site', models.Model),
            managers=[
                ('objects', mainsite.models.CachedSiteManager()),
            ],
        ),
    ]