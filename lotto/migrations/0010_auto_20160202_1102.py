# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 11:02
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0009_auto_20160202_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lotterytype',
            name='rollover',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20),
        ),
    ]