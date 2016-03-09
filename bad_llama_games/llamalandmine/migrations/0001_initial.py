# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
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
                ('tier', models.IntegerField()),
                ('icon', models.ImageField(default=b'H:/Year2/Internet Technology/LlamaLandmine/bad_llama_games\\static\\images\\Llama.png', upload_to=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score_to_beat', models.IntegerField()),
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
                ('date_played', models.DateField(default=datetime.date.today)),
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
                ('picture', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('games_played_easy', models.IntegerField(default=0)),
                ('games_played_medium', models.IntegerField(default=0)),
                ('games_played_hard', models.IntegerField(default=0)),
                ('best_score_easy', models.IntegerField(default=0)),
                ('best_score_medium', models.IntegerField(default=0)),
                ('best_score_hard', models.IntegerField(default=0)),
                ('earned_badges', models.ManyToManyField(to='llamalandmine.Badge')),
                ('friends', models.ManyToManyField(related_name='friends_rel_+', to='llamalandmine.RegisteredUser')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='game',
            name='user',
            field=models.OneToOneField(related_name='current_game', to='llamalandmine.RegisteredUser'),
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
            name='challenger',
            field=models.ForeignKey(related_name='challenges_created', to='llamalandmine.RegisteredUser'),
            preserve_default=True,
        ),
    ]
