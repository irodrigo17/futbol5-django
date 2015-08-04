# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from core.models import Player


def generate_users(apps, schema_editor):
    for player in Player.objects.all():
        player.user = player.create_user()
        player.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150722_2325'),
    ]

    operations = [
        migrations.RunPython(generate_users),
    ]
