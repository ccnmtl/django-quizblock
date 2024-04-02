from __future__ import unicode_literals

from django.urls import re_path
from .views import (
    EditQuizView, DeleteQuestionView, DeleteAnswerView,
    ReorderAnswersView, ReorderQuestionsView,
    AddQuestionToQuizView, EditQuestionView,
    AddAnswerToQuestionView, EditAnswerView,
)

urlpatterns = [
    re_path(r'^edit_quiz/(?P<pk>\d+)/$', EditQuizView.as_view(), {},
            'edit-quiz'),
    re_path(r'^edit_quiz/(?P<pk>\d+)/add_question/$',
            AddQuestionToQuizView.as_view(), {}, 'add-question-to-quiz'),
    re_path(r'^edit_question/(?P<pk>\d+)/$', EditQuestionView.as_view(), {},
            'edit-question'),
    re_path(r'^edit_question/(?P<pk>\d+)/add_answer/$',
            AddAnswerToQuestionView.as_view(), {}, 'add-answer-to-question'),
    re_path(r'^delete_question/(?P<pk>\d+)/$', DeleteQuestionView.as_view(),
            {}, 'delete-question'),
    re_path(r'^reorder_answers/(?P<pk>\d+)/$', ReorderAnswersView.as_view(),
            {}, 'reorder-answer'),
    re_path(r'^reorder_questions/(?P<pk>\d+)/$',
            ReorderQuestionsView.as_view(), {}, 'reorder-questions'),
    re_path(r'^delete_answer/(?P<pk>\d+)/$', DeleteAnswerView.as_view(),
            {}, 'delete-answer'),
    re_path(r'^edit_answer/(?P<pk>\d+)/$', EditAnswerView.as_view(),
            {}, 'edit-answer'),
]
