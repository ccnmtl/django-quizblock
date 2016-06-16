# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '0005_re_add_show_submit_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={},
        ),
    ]
