# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-01 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0002_auto_20160201_1126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='win',
            name='punter',
        ),
        migrations.AlterField(
            model_name='lotterytype',
            name='max_val',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='lotterytype',
            name='number_of_numbers',
            field=models.PositiveIntegerField(),
        ),
    ]