from django.test import TestCase
from django.test.client import RequestFactory
from pagetree.tests.factories import UserFactory
from quizblock.models import Quiz, Question, Answer
from quizblock.views import EditQuizView, AddQuestionToQuizView, \
    EditQuestionView, AddAnswerToQuestionView, DeleteQuestionView, \
    DeleteAnswerView, EditAnswerView, ReorderAnswersView, ReorderQuestionsView


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

        question = self.quiz.question_set.get(text="the text")
        self.assertEquals(question.intro_text, 'the intro')
        self.assertEquals(question.explanation, 'the explanation')
        self.assertEquals(question.question_type, 'short text')

    def test_edit_question(self):
        question = self.quiz.question_set.all()[0]
        url = "/quizblock/edit_question/%s/" % question.id

        data = {u'text': [u'alt text'],
                u'intro_text': [u'alt intro'],
                u'explanation': [u'alt explanation'],
                u'question_type': [u'short text']}
        request = self.factory.post(url, data)
        request.user = self.user

        response = EditQuestionView.as_view()(request, pk=question.id)
        self.assertEquals(response.status_code, 302)

        question = self.quiz.question_set.all()[0]
        self.assertEquals(question.intro_text, 'alt intro')
        self.assertEquals(question.explanation, 'alt explanation')
        self.assertEquals(question.question_type, 'short text')

    def test_add_answer_to_question(self):
        question = self.quiz.question_set.all()[0]
        self.assertEquals(question.answer_set.count(), 2)
        url = '/quizblock/edit_question/%s/add_answer/' % question.id

        data = {u'explanation': [u'the explanation'],
                u'value': [u'2'],
                u'label': [u'Maybe']}
        request = self.factory.post(url, data)
        request.user = self.user

        response = AddAnswerToQuestionView.as_view()(request, pk=question.id)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(question.answer_set.count(), 3)
        answer = question.answer_set.get(label='Maybe')
        self.assertEquals(answer.explanation, 'the explanation')
        self.assertEquals(answer.value, '2')

    def test_add_answer_to_question_emptylabel(self):
        question = self.quiz.question_set.all()[0]
        url = '/quizblock/edit_question/%s/add_answer/' % question.id

        data = {u'explanation': [u'the explanation'],
                u'value': [u'Maybe']}
        request = self.factory.post(url, data)
        request.user = self.user

        response = AddAnswerToQuestionView.as_view()(request, pk=question.id)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(question.answer_set.count(), 3)
        question.answer_set.get(label='Maybe')

    def test_delete_question(self):
        question = self.quiz.question_set.all()[0]
        url = '/quizblock/delete_question/%s/' % question.id

        request = self.factory.post(url, {})
        request.user = self.user

        response = DeleteQuestionView.as_view()(request, pk=question.id)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(self.quiz.question_set.count(), 0)

    def test_reorder_answers(self):
        question = self.quiz.question_set.all()[0]

        yes = Answer.objects.get(label='Yes')
        self.assertEquals(yes.display_number(), 1)
        no = Answer.objects.get(label='No')
        self.assertEquals(no.display_number(), 2)

        args = 'answer_0=%s&answer_1=%s' % (yes.id, no.id)
        url = '/quizblock/reorder_answers/%s/?%s' % (question.id, args)
        request = self.factory.post(url, {})
        request.user = self.user

        response = ReorderAnswersView.as_view()(request, pk=question.id)
        self.assertEquals(response.status_code, 200)

        yes = Answer.objects.get(label='Yes')
        self.assertEquals(yes.display_number(), 1)
        no = Answer.objects.get(label='No')
        self.assertEquals(no.display_number(), 2)

    def test_reorder_questions(self):
        self.short_text = Question.objects.create(
            quiz=self.quiz, text='short text', question_type='short text')

        self.assertEqual(self.single_answer.display_number(), 1)
        self.assertEqual(self.short_text.display_number(), 2)

        args = 'question_0=%s&question_1=%s' % (self.short_text.id,
                                                self.single_answer.id)
        url = '/quizblock/reorder_questions/%s/?%s' % (self.quiz.id, args)
        request = self.factory.post(url)
        request.user = self.user

        response = ReorderQuestionsView.as_view()(request, pk=self.quiz.id)
        self.assertEquals(response.status_code, 200)

        self.short_text = Question.objects.get(text='short text')
        self.assertEqual(self.short_text.display_number(), 1)
        self.single_answer = Question.objects.get(text='single answer')
        self.assertEqual(self.single_answer.display_number(), 2)

    def test_delete_answer(self):
        question = self.quiz.question_set.all()[0]
        self.assertEquals(question.answer_set.count(), 2)
        answer = question.answer_set.all()[0]
        url = '/quizblock/delete_answer/%s/' % answer.id

        request = self.factory.post(url, {})
        request.user = self.user

        response = DeleteAnswerView.as_view()(request, pk=answer.id)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(question.answer_set.count(), 1)

    def test_edit_answer(self):
        question = self.quiz.question_set.all()[0]
        answer = question.answer_set.all()[0]
        url = "/quizblock/edit_answer/%s/" % answer.id

        data = {u'explanation': [u'alt explanation'],
                u'value': [u'Possibly']}
        request = self.factory.post(url, data)
        request.user = self.user

        response = EditAnswerView.as_view()(request, pk=answer.id)
        self.assertEquals(response.status_code, 302)

        answer = question.answer_set.get(value='Possibly')
        self.assertEquals(answer.explanation, 'alt explanation')
