# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0002_challenge_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registereduser',
            name='picture',
            field=models.ImageField(upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
