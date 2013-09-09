from django.test import TestCase
from quizblock.models import Quiz, Question, Answer, Submission
from quizblock.models import Response
from quizblock.templatetags.getresponse import GetQuestionResponseNode
from quizblock.templatetags.getresponse import IfAnswerInNode
from django.contrib.auth.models import User


class FakeRequest(object):
    pass


class GetQuestionResponseNodeTest(TestCase):
    def test_render(self):
        q = Quiz.objects.create()
        question = Question.objects.create(
            quiz=q, text="a question", question_type='long text')
        u = User.objects.create(username="testuser")
        submission = Submission.objects.create(
            quiz=q,
            user=u)
        response = Response.objects.create(
            submission=submission,
            question=question,
            value="a long text response")
        n = GetQuestionResponseNode('question', "foo")
        r = FakeRequest()
        r.user = u
        context = dict(request=r, question=question)
        out = n.render(context)
        self.assertEqual(out, '')
        self.assertTrue('foo' in context)
        self.assertEqual(context['foo'], response)

    def test_render_no_submission(self):
        q = Quiz.objects.create()
        question = Question.objects.create(
            quiz=q, text="a question", question_type='long text')
        u = User.objects.create(username="testuser")
        n = GetQuestionResponseNode('question', "foo")
        r = FakeRequest()
        r.user = u
        context = dict(request=r, question=question)
        out = n.render(context)
        self.assertEqual(out, '')
        self.assertFalse('foo' in context)

    def test_render_submission_but_no_response(self):
        q = Quiz.objects.create()
        question = Question.objects.create(
            quiz=q, text="a question", question_type='long text')
        u = User.objects.create(username="testuser")
        Submission.objects.create(
            quiz=q,
            user=u)
        n = GetQuestionResponseNode('question', "foo")
        r = FakeRequest()
        r.user = u
        context = dict(request=r, question=question)
        out = n.render(context)
        self.assertEqual(out, '')
        self.assertTrue('foo' in context)
        self.assertEqual(context['foo'], None)


class MockNodeList(object):
    def __init__(self):
        self.rendered = False

    def render(self, c):
        self.rendered = True


class IfAnswerInTest(TestCase):
    def test_render_true(self):
        q = Quiz.objects.create()
        question = Question.objects.create(
            quiz=q, text="a question", question_type='single choice')
        answer = Answer.objects.create(question=question,
                                       value='1', label='one')
        u = User.objects.create(username="testuser")
        submission = Submission.objects.create(
            quiz=q,
            user=u)
        response = Response.objects.create(
            submission=submission,
            question=question,
            value="1")
        nl1 = MockNodeList()
        nl2 = MockNodeList()
        n = IfAnswerInNode('response', 'answer', nl1, nl2)
        r = FakeRequest()
        r.user = u
        context = dict(request=r, question=question, answer=answer,
                       response=response)
        out = n.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nl1.rendered)
        self.assertFalse(nl2.rendered)

    def test_render_false(self):
        q = Quiz.objects.create()
        question = Question.objects.create(
            quiz=q, text="a question", question_type='single choice')
        Answer.objects.create(
            question=question,
            value='1', label='one')
        answer2 = Answer.objects.create(
            question=question,
            value='2', label='two')
        u = User.objects.create(username="testuser")
        submission = Submission.objects.create(
            quiz=q,
            user=u)
        response = Response.objects.create(
            submission=submission,
            question=question,
            value="1")
        nl1 = MockNodeList()
        nl2 = MockNodeList()
        n = IfAnswerInNode('response', 'answer', nl1, nl2)
        r = FakeRequest()
        r.user = u
        context = dict(request=r, question=question, answer=answer2,
                       response=response)
        out = n.render(context)
        self.assertEqual(out, None)
        self.assertFalse(nl1.rendered)
        self.assertTrue(nl2.rendered)
