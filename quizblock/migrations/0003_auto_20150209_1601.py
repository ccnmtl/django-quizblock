# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '0002_auto_20150202_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='css_extra',
            field=models.CharField(help_text=b'extra CSS classes (space separated)', max_length=256, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(help_text=b'Required'),
            preserve_default=True,
        ),
    ]
