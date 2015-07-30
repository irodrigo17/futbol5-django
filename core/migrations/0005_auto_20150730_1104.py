# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_weeklymatchschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklymatchschedule',
            name='invite_weekday',
            field=models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)], default=0, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='weeklymatchschedule',
            name='weekday',
            field=models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)], choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]),
        ),
    ]
