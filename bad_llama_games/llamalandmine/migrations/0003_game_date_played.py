# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0002_auto_20160314_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='date_played',
            field=models.DateField(default=datetime.datetime(2016, 3, 14, 15, 46, 36, 149000)),
            preserve_default=True,
        ),
    ]
