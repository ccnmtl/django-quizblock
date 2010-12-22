from django.conf.urls.defaults import patterns

urlpatterns = patterns('quizblock.views',
                       (r'^edit_quiz/(?P<id>\d+)/$','edit_quiz',{},'edit-quiz'),
                       (r'^edit_quiz/(?P<id>\d+)/add_question/$','add_question_to_quiz',{},'add-question-to-quiz'),
                       (r'^edit_question/(?P<id>\d+)/$','edit_question',{},'edit-question'),
                       (r'^edit_question/(?P<id>\d+)/add_answer/$','add_answer_to_question',{},'add-answer-to-question'),
                       (r'^delete_question/(?P<id>\d+)/$','delete_question',{},'delete-question'),
                       (r'^reorder_answers/(?P<id>\d+)/$','reorder_answers',{},'reorder-answer'),
                       (r'^reorder_questions/(?P<id>\d+)/$','reorder_questions',{},'reorder-questions'),
                       (r'^delete_answer/(?P<id>\d+)/$','delete_answer',{},'delete-answer'),
                       (r'^edit_answer/(?P<id>\d+)/$','edit_answer',{},'edit-answer'),
)
