# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0003_game_date_played'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='date_played',
            field=models.DateField(default=datetime.datetime(2016, 3, 14, 16, 45, 49, 879000)),
            preserve_default=True,
        ),
    ]
