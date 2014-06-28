from django.conf.urls import patterns
from .views import (
    EditQuizView, DeleteQuestionView, DeleteAnswerView,
    ReorderAnswersView, ReorderQuestionsView,
    AddQuestionToQuizView, EditQuestionView,
    AddAnswerToQuestionView, EditAnswerView,
)

urlpatterns = patterns(
    'quizblock.views',
    (r'^edit_quiz/(?P<pk>\d+)/$', EditQuizView.as_view(), {}, 'edit-quiz'),
    (r'^edit_quiz/(?P<pk>\d+)/add_question/$', AddQuestionToQuizView.as_view(),
     {}, 'add-question-to-quiz'),
    (r'^edit_question/(?P<pk>\d+)/$', EditQuestionView.as_view(), {},
     'edit-question'),
    (r'^edit_question/(?P<pk>\d+)/add_answer/$',
     AddAnswerToQuestionView.as_view(), {}, 'add-answer-to-question'),
    (r'^delete_question/(?P<pk>\d+)/$', DeleteQuestionView.as_view(), {},
     'delete-question'),
    (r'^reorder_answers/(?P<pk>\d+)/$', ReorderAnswersView.as_view(), {},
     'reorder-answer'),
    (r'^reorder_questions/(?P<pk>\d+)/$', ReorderQuestionsView.as_view(), {},
     'reorder-questions'),
    (r'^delete_answer/(?P<pk>\d+)/$', DeleteAnswerView.as_view(),
     {}, 'delete-answer'),
    (r'^edit_answer/(?P<pk>\d+)/$', EditAnswerView.as_view(),
     {}, 'edit-answer'),
)
