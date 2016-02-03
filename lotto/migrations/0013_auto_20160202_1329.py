# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 13:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0012_simplelottery'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoreComplexLottery',
            fields=[
                ('lotterytype_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lotto.LotteryType')),
                ('spotprize_nummatches', models.PositiveIntegerField()),
                ('spotprize_value', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
            options={
                'verbose_name': 'More Complex Lottery Type',
                'verbose_name_plural': 'More Complex Lottery Types',
            },
            bases=('lotto.lotterytype',),
        ),
        migrations.AlterModelOptions(
            name='simplelottery',
            options={'verbose_name': 'Simple Lottery Type', 'verbose_name_plural': 'Simple Lottery Types'},
        ),
    ]