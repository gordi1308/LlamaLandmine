# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0005_auto_20160314_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='date_played',
            field=models.DateField(default=datetime.datetime(2016, 3, 14, 18, 6, 40, 230000)),
            preserve_default=True,
        ),
    ]
