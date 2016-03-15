# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registereduser',
            name='best_score_easy',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='best_score_hard',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='best_score_medium',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='games_played_easy',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='games_played_hard',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='games_played_medium',
        ),
    ]
