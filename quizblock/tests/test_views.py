from django.test import TestCase
from django.test.client import RequestFactory
from pagetree.tests.factories import UserFactory
from quizblock.models import Quiz, Question, Answer
from quizblock.views import EditQuizView, AddQuestionToQuizView


class LoggedInViewTest(TestCase):
    urls = 'quizblock.urls'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()

        self.quiz = Quiz()
        self.quiz.save()

        self.single_answer = Question.objects.create(
            quiz=self.quiz, text='single answer',
            question_type='single choice')
        self.single_answer_one = Answer.objects.create(
            question=self.single_answer, label='Yes', value='1')
        self.single_answer_two = Answer.objects.create(
            question=self.single_answer, label='No', value='0')

    def test_edit_quiz(self):
        url = "/quizblock/edit_quiz/%s/" % self.quiz.id
        request = self.factory.get(url)
        request.user = self.user

        response = EditQuizView.as_view()(request, pk=self.quiz.id)
        self.assertEqual(response.status_code, 200)

    def test_add_question_to_quiz(self):
        self.assertEquals(self.quiz.question_set.count(), 1)
        url = "/quizblock/edit_quiz/%s/add_question" % self.quiz.id

        data = {u'text': [u'the text'],
                u'intro_text': [u'the intro'],
                u'explanation': [u'the explanation'],
                u'question_type': [u'short text']}
        request = self.factory.post(url, data)
        request.user = self.user

        response = AddQuestionToQuizView.as_view()(request, pk=self.quiz.id)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.quiz.question_set.count(), 2)

#     def test_edit_question(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_add_answer_to_question(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_delete_question(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_reorder_answers(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_reorder_questions(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_delete_answer(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
# 
#     def test_edit_answer(self):
#         response = self.client.get("/")
#         self.assertEquals(response.status_code, 200)
