# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-04 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0017_auto_20160204_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='punter',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
