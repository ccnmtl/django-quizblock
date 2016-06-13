from __future__ import unicode_literals

from django.conf.urls import url
from .views import (
    EditQuizView, DeleteQuestionView, DeleteAnswerView,
    ReorderAnswersView, ReorderQuestionsView,
    AddQuestionToQuizView, EditQuestionView,
    AddAnswerToQuestionView, EditAnswerView,
)

urlpatterns = [
    url(r'^edit_quiz/(?P<pk>\d+)/$', EditQuizView.as_view(), {}, 'edit-quiz'),
    url(r'^edit_quiz/(?P<pk>\d+)/add_question/$',
        AddQuestionToQuizView.as_view(), {}, 'add-question-to-quiz'),
    url(r'^edit_question/(?P<pk>\d+)/$', EditQuestionView.as_view(), {},
        'edit-question'),
    url(r'^edit_question/(?P<pk>\d+)/add_answer/$',
        AddAnswerToQuestionView.as_view(), {}, 'add-answer-to-question'),
    url(r'^delete_question/(?P<pk>\d+)/$', DeleteQuestionView.as_view(), {},
        'delete-question'),
    url(r'^reorder_answers/(?P<pk>\d+)/$', ReorderAnswersView.as_view(), {},
        'reorder-answer'),
    url(r'^reorder_questions/(?P<pk>\d+)/$', ReorderQuestionsView.as_view(),
        {}, 'reorder-questions'),
    url(r'^delete_answer/(?P<pk>\d+)/$', DeleteAnswerView.as_view(),
        {}, 'delete-answer'),
    url(r'^edit_answer/(?P<pk>\d+)/$', EditAnswerView.as_view(),
        {}, 'edit-answer'),
]
