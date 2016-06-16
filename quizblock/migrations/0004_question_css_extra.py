# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '0003_auto_20150209_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='css_extra',
            field=models.TextField(help_text=b'extra CSS classes (space separated)', null=True, blank=True),
            preserve_default=True,
        ),
    ]
