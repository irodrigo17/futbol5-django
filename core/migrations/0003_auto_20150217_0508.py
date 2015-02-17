# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150210_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('inviting_date', models.DateTimeField(auto_now_add=True)),
                ('inviting_player', models.ForeignKey(to='core.Player')),
                ('match', models.ForeignKey(related_name='guests', to='core.Match')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='guest',
            unique_together=set([('match', 'inviting_player', 'name')]),
        ),
    ]
