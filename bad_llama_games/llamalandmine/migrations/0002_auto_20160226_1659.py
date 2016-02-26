# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('llamalandmine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='challenged_user',
            field=models.ForeignKey(related_name='challenged_received', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='challenger',
            field=models.ForeignKey(related_name='challenges_created', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='game',
            name='user',
            field=models.OneToOneField(related_name='current_game', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='friends',
            field=models.ManyToManyField(related_name='friends_rel_+', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
    ]
