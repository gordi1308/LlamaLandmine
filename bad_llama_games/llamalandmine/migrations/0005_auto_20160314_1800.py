# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0004_auto_20160314_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='date_played',
            field=models.DateField(default=datetime.datetime(2016, 3, 14, 18, 0, 25, 253000)),
            preserve_default=True,
        ),
    ]
