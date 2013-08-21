from django.test import TestCase
from quizblock.models import Quiz, Question, Answer, Submission
from quizblock.models import Response
from django.contrib.auth.models import User


class FakeReq(object):
    def __init__(self):
        self.POST = dict()


class TestBasics(TestCase):
    def test_create(self):
        q = Quiz()
        self.assertNotEqual(q, None)

    def test_needs_submit(self):
        q = Quiz()
        self.assertTrue(q.needs_submit())
        q.rhetorical = True
        self.assertFalse(q.needs_submit())

    def test_add_form(self):
        f = Quiz.add_form()
        self.assertTrue('rhetorical' in f.fields)
        self.assertTrue('allow_redo' in f.fields)

    def test_create_method(self):
        r = FakeReq()
        q = Quiz.create(r)
        self.assertEquals(q.description, '')
        self.assertEquals(q.display_name, 'Quiz')

    def test_dict_roundtrip(self):
        q1 = Quiz(description="first")
        d = q1.as_dict()
        q2 = Quiz(description="second")
        q2.import_from_dict(d)
        self.assertEquals(q2.description, "first")
        self.assertEquals(q1.allow_redo, q2.allow_redo)
        self.assertEquals(q1.rhetorical, q2.rhetorical)

    def test_create_from_dict(self):
        q = Quiz(description="first")
        d = q.as_dict()
        q2 = Quiz.create_from_dict(d)
        self.assertEquals(q2.description, "first")
        self.assertEquals(q.allow_redo, q2.allow_redo)
        self.assertEquals(q.rhetorical, q2.rhetorical)

    def test_summary_render(self):
        q = Quiz(description="short")
        self.assertEqual(q.summary_render(), "short")
        q.description = ''.join(str(x) for x in range(75))
        expected = ('012345678910111213141516171819202122'
                    '2324252627282930313233343...')
        self.assertEqual(q.summary_render(), expected)

    def test_edit(self):
        q = Quiz()
        q.edit(dict(description='foo', rhetorical='1', allow_redo='0'), None)
        self.assertEqual(q.description, 'foo')
        self.assertEqual(q.rhetorical, '1')
        self.assertEqual(q.allow_redo, '0')


class UserTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")

    def test_submit(self):
        q = Quiz.objects.create()
        self.assertFalse(q.unlocked(self.u))
        q.submit(self.u, dict())
        self.assertTrue(q.unlocked(self.u))
        q.clear_user_submissions(self.u)
        self.assertFalse(q.unlocked(self.u))


class QuestionTest(TestCase):
    def test_unicode(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(str(question), "foo")

    def test_display_number(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.display_number(), 1)

    def test_edit_form(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        f = question.edit_form()
        self.assertTrue('question_type' in f.fields)

    def test_add_answer_form(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        f = question.add_answer_form()
        self.assertTrue(hasattr(f, 'fields'))

    def test_correct_answer_values(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.correct_answer_values(), [])

    def test_correct_answer_number(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.correct_answer_number(), None)

    def test_correct_answer_letter(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.correct_answer_letter(), None)

    def test_update_answers_order(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        question.update_answers_order([])

    def test_answerable(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertFalse(question.answerable())
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        self.assertTrue(question.answerable())

    def test_types(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertFalse(question.is_short_text())
        self.assertTrue(question.is_long_text())
        self.assertFalse(question.is_single_choice())
        self.assertFalse(question.is_single_choice_dropdown())
        self.assertFalse(question.is_multiple_choice())

    def test_as_dict(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        d = question.as_dict()
        self.assertEqual(d['text'], "foo")
        self.assertEqual(d['question_type'], "long text")


class AnswerTest(TestCase):
    def test_unicode(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        answer = Answer.objects.create(question=question, label="an answer")
        self.assertEqual(str(answer), "an answer")

    def test_edit_form(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        answer = Answer.objects.create(question=question, label="an answer")
        f = answer.edit_form()
        self.assertTrue('label' in f.fields)

    def test_as_dict(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        answer = Answer.objects.create(question=question, label="an answer")
        d = answer.as_dict()
        self.assertEqual(d['label'], "an answer")
        self.assertFalse(d['correct'])


class SubmissionTest(TestCase):
    def test_unicode(self):
        quiz = Quiz.objects.create()
        user = User.objects.create(username="testuser")
        s = Submission.objects.create(quiz=quiz, user=user)
        self.assertTrue(
            str(s).startswith("quiz %d submission by testuser" % quiz.id))


class ResponseTest(TestCase):
    def test_unicode(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        Answer.objects.create(question=question, label="an answer")
        user = User.objects.create(username="testuser")
        s = Submission.objects.create(quiz=quiz, user=user)
        response = Response.objects.create(
            question=question, submission=s, value="an answer")
        self.assertTrue(str(response).startswith("response to "))

    def test_is_correct(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        Answer.objects.create(question=question, label="an answer")
        user = User.objects.create(username="testuser")
        s = Submission.objects.create(quiz=quiz, user=user)
        response = Response.objects.create(
            question=question, submission=s, value="an answer")
        self.assertFalse(response.is_correct())
