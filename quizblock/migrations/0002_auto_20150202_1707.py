# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
