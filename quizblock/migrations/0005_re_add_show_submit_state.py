# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, utils


class FailsafeAddField(migrations.AddField):
    def database_forwards(self, app_label, schema_editor, from_state,
                          to_state):
        try:
            super(FailsafeAddField, self).database_forwards(
                app_label, schema_editor, from_state, to_state)
        except utils.ProgrammingError:
            # This column must have already been added by the
            # initial migration, so don't do anything.
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '0004_question_css_extra'),
    ]

    operations = [
        FailsafeAddField('Quiz', 'show_submit_state',
                         models.BooleanField(default=True))
    ]
