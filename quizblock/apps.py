from __future__ import unicode_literals

from django.apps import AppConfig


class QuizBlockConfig(AppConfig):
    name = 'quizblock'
    verbose_name = "Quizblock"

    def ready(self):
        from pagetree.reports import ReportableInterface
        ReportableInterface.register(self.get_model('Quiz'))
