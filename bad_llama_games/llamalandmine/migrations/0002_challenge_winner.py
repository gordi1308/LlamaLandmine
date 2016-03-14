# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='winner',
            field=models.ForeignKey(related_name='challenges_won', to='llamalandmine.RegisteredUser', null=True),
            preserve_default=True,
        ),
    ]
