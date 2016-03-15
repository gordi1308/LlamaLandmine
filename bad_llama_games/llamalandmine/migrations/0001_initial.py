# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('tier', models.IntegerField(default=1)),
                ('icon', models.ImageField(upload_to=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('remaining_attempts', models.IntegerField(default=5)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(max_length=6)),
                ('was_won', models.BooleanField(default=False)),
                ('score', models.IntegerField(default=0)),
                ('time_taken', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegisteredUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.ImageField(upload_to=b'', blank=True)),
                ('games_played_easy', models.IntegerField(default=0)),
                ('games_played_medium', models.IntegerField(default=0)),
                ('games_played_hard', models.IntegerField(default=0)),
                ('best_score_easy', models.IntegerField(default=0)),
                ('best_score_medium', models.IntegerField(default=0)),
                ('best_score_hard', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('badge', models.ForeignKey(to='llamalandmine.Badge')),
                ('user', models.ForeignKey(to='llamalandmine.RegisteredUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserFriend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friend', models.ForeignKey(related_name='friend', to='llamalandmine.RegisteredUser')),
                ('user', models.ForeignKey(to='llamalandmine.RegisteredUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='earned_badges',
            field=models.ManyToManyField(to='llamalandmine.Badge', through='llamalandmine.UserBadge'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registereduser',
            name='friends',
            field=models.ManyToManyField(to='llamalandmine.RegisteredUser', through='llamalandmine.UserFriend'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registereduser',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='user',
            field=models.ForeignKey(related_name='game', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='challenged_user',
            field=models.ForeignKey(related_name='challenges_received', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='game',
            field=models.ForeignKey(related_name='challenge', to='llamalandmine.Game'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='winner',
            field=models.ForeignKey(related_name='challenges_won', to='llamalandmine.RegisteredUser', null=True),
            preserve_default=True,
        ),
    ]
