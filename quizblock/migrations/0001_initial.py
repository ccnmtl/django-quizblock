# flake8: noqa
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
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=256)),
                ('label', models.TextField(blank=True)),
                ('correct', models.BooleanField(default=False)),
                ('explanation', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('question',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('question_type', models.CharField(max_length=256, choices=[(b'multiple choice', b'Multiple Choice: Multiple answers'), (b'single choice', b'Multiple Choice: Single answer'), (b'single choice dropdown', b'Multiple Choice: Single answer (dropdown)'), (b'short text', b'Short Text'), (b'long text', b'Long Text')])),
                ('explanation', models.TextField(blank=True)),
                ('intro_text', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('quiz',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(blank=True)),
                ('rhetorical', models.BooleanField(default=False)),
                ('allow_redo', models.BooleanField(default=True)),
                ('show_submit_state', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(blank=True)),
                ('question', models.ForeignKey(to='quizblock.Question')),
            ],
            options={
                'ordering': ('question',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(default=datetime.datetime.now)),
                ('quiz', models.ForeignKey(to='quizblock.Quiz')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='response',
            name='submission',
            field=models.ForeignKey(to='quizblock.Submission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(to='quizblock.Quiz'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='question',
            order_with_respect_to='quiz',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='quizblock.Question'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='answer',
            order_with_respect_to='question',
        ),
    ]
