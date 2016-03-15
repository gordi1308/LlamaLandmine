# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0006_auto_20160314_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='date_played',
            field=models.DateField(default=datetime.datetime(2016, 3, 14, 18, 7, 38, 475000)),
            preserve_default=True,
        ),
    ]
