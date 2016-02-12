# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-12 05:36
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('wlmuser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyGroup',
            fields=[
            ],
            options={
                'verbose_name': 'Group',
                'proxy': True,
                'verbose_name_plural': 'Groups',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
    ]
