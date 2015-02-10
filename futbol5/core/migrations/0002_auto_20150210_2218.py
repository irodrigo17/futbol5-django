# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(to='core.Player', through='core.MatchPlayer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='matches',
            field=models.ManyToManyField(to='core.Match', through='core.MatchPlayer'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='date',
            field=models.DateTimeField(unique=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='email',
            field=models.CharField(db_index=True, unique=True, max_length=50, validators=[django.core.validators.EmailValidator()]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='matchplayer',
            unique_together=set([('match', 'player')]),
        ),
    ]
