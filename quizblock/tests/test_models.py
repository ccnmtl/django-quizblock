from __future__ import unicode_literals

from django.test import TestCase
from quizblock.models import Quiz, Question, Answer, Submission
from quizblock.models import Response
from django.contrib.auth.models import User
from django.utils.encoding import smart_str


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
        self.assertTrue('show_submit_state' in f.fields)

    def test_create_method(self):
        r = FakeReq()
        q = Quiz.create(r)
        self.assertEquals(q.description, '')
        self.assertEquals(q.display_name, 'Quiz')
        self.assertFalse(q.show_submit_state)
        self.assertFalse(q.rhetorical)
        self.assertFalse(q.allow_redo)

    def test_create_method_two(self):
        r = FakeReq()
        r.POST['show_submit_state'] = 'on'
        r.POST['rhetorical'] = 'on'
        r.POST['allow_redo'] = 'on'
        q = Quiz.create(r)
        self.assertEquals(q.description, '')
        self.assertEquals(q.display_name, 'Quiz')
        self.assertTrue(q.show_submit_state)
        self.assertTrue(q.rhetorical)
        self.assertTrue(q.allow_redo)

    def test_dict_roundtrip(self):
        q1 = Quiz(description="first", show_submit_state=False)
        d = q1.as_dict()
        q2 = Quiz(description="second")
        q2.import_from_dict(d)
        self.assertEquals(q2.description, "first")
        self.assertEquals(q1.allow_redo, q2.allow_redo)
        self.assertEquals(q1.rhetorical, q2.rhetorical)
        self.assertEquals(q1.show_submit_state, q2.show_submit_state)

    def test_create_from_dict(self):
        q = Quiz(description="first")
        d = q.as_dict()
        q2 = Quiz.create_from_dict(d)
        self.assertEquals(q2.description, "first")
        self.assertEquals(q.allow_redo, q2.allow_redo)
        self.assertEquals(q.rhetorical, q2.rhetorical)
        self.assertEquals(q.show_submit_state, q2.show_submit_state)

    def test_create_from_dict_defaults(self):
        d = {
            'description': 'Test Quiz',
        }
        q = Quiz.create_from_dict(d)
        self.assertEquals(q.description, 'Test Quiz')
        self.assertEquals(q.allow_redo, True)
        self.assertEquals(q.rhetorical, False)
        self.assertEquals(q.show_submit_state, True)

    def test_import_from_dict_defaults(self):
        d = {
            'description': 'Test Quiz',
        }
        q = Quiz()
        q.import_from_dict(d)
        self.assertEqual(q.description, 'Test Quiz')
        self.assertEqual(q.allow_redo, True)
        self.assertEqual(q.rhetorical, False)
        self.assertEqual(q.show_submit_state, True)
        self.assertEqual(q.submission_set.count(), 0)
        self.assertEqual(q.question_set.count(), 0)

    def test_import_from_dict_defaults_2(self):
        d = {
            'description': 'Test Quiz',
            'rhetorical': False,
            'allow_redo': False,
            'show_submit_state': True,
            'questions': [{
                'text': 'Test Question',
                'question_type': 'single choice',
                'explanation': '',
                'answers': [],
            }],
        }
        q = Quiz()
        q.import_from_dict(d)
        self.assertEqual(q.description, 'Test Quiz')
        self.assertEqual(q.allow_redo, False)
        self.assertEqual(q.rhetorical, False)
        self.assertEqual(q.show_submit_state, True)
        self.assertEqual(q.submission_set.count(), 0)
        self.assertEqual(q.question_set.count(), 1)
        self.assertEqual(q.question_set.first().intro_text, '')

    def test_summary_render(self):
        q = Quiz(description="short")
        self.assertEqual(q.summary_render(), "short")
        q.description = ''.join(smart_str(x) for x in range(75))
        expected = ('012345678910111213141516171819202122'
                    '2324252627282930313233343...')
        self.assertEqual(q.summary_render(), expected)

    def test_edit(self):
        q = Quiz()
        q.edit(dict(description='foo', rhetorical='on',
                    allow_redo='0', show_submit_state='on'), None)
        self.assertEqual(q.description, 'foo')
        self.assertEqual(q.rhetorical, True)
        self.assertEqual(q.allow_redo, False)
        self.assertTrue(q.show_submit_state)

    def test_edit_two(self):
        q = Quiz()
        q.edit(dict(description='foo'), None)
        self.assertEqual(q.description, 'foo')
        self.assertFalse(q.rhetorical)
        self.assertFalse(q.allow_redo)
        self.assertFalse(q.show_submit_state)

    def test_edit_form(self):
        # can't figure out how to test this one since it depends on
        # urls being set up

        # q = Quiz()
        # f = q.edit_form()
        # self.assertTrue('description' in f.fields)
        pass

    def test_redirect_to_self_on_submit(self):
        q = Quiz()
        self.assertTrue(q.redirect_to_self_on_submit())

        q2 = Quiz(show_submit_state=False)
        self.assertFalse(q2.redirect_to_self_on_submit())

    def test_add_question_form(self):
        q = Quiz()
        f = q.add_question_form(None)
        self.assertTrue('text' in f.fields)


class UserTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")

    def test_submit(self):
        q = Quiz.objects.create()
        self.assertFalse(q.unlocked(self.u))
        q.submit(self.u, dict(foo='bar'))
        self.assertTrue(q.unlocked(self.u))
        q.clear_user_submissions(self.u)
        self.assertFalse(q.unlocked(self.u))


class QuestionTest(TestCase):
    def test_str(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(smart_str(question), "foo")

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

    def test_correct_answer_number_wrong_type(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.correct_answer_number(), None)

    def test_correct_answer_number(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        Answer.objects.create(question=question, value='1', label='one',
                              correct=True)
        self.assertEqual(question.correct_answer_number(), 0)

    def test_correct_answer_letter_wrong_type(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")
        self.assertEqual(question.correct_answer_letter(), None)

    def test_correct_answer_letter(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        Answer.objects.create(question=question, value='1', label='one',
                              correct=True)
        self.assertEqual(question.correct_answer_letter(), 'A')

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

    def test_user_responses(self):
        user = User.objects.create(username="testuser")
        quiz = Quiz.objects.create()
        q1 = Question.objects.create(quiz=quiz, text="question_one",
                                     question_type="single choice")
        Answer.objects.create(question=q1, label="a", value="a", correct=True)
        Answer.objects.create(question=q1, label="b", value="b")

        self.assertEquals(len(q1.user_responses(user)), 0)

        s = Submission.objects.create(quiz=quiz, user=user)
        self.assertEquals(len(q1.user_responses(user)), 0)

        Response.objects.create(question=q1, submission=s, value="a")
        self.assertEquals(len(q1.user_responses(user)), 1)


class TestIsUserCorrect(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create()

    def test_no_questions(self):
        self.assertEquals(self.quiz.score(self.user), None)

    def test_short_text(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="short text")

        # no submissions
        self.assertIsNone(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), None)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="a")

        self.assertTrue(question.is_user_correct(self.user))

        # score
        self.assertEquals(self.quiz.score(self.user), 1)

    def test_long_text(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="long text")

        # no submissions
        self.assertIsNone(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), None)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="b")

        self.assertTrue(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 1)

    def test_single_choice_no_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="single choice")
        Answer.objects.create(question=question, label="a", value="a")
        Answer.objects.create(question=question, label="b", value="b")
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertIsNone(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), None)

        # user responded
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="b")

        self.assertTrue(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 1)

    def test_single_choice_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="single choice")
        Answer.objects.create(question=question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=question, label="b", value="b")
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), None)

        # user responded
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        response = Response.objects.create(question=question,
                                           submission=sub, value="a")

        self.assertTrue(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 1)

        response.value = 'b'
        response.save()
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 0)

    def test_multiple_choice_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="multiple choice")
        Answer.objects.create(question=question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=question, label="b", value="b",
                              correct=True)
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), None)

        # user responded - incorrectly
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        c = Response.objects.create(question=question,
                                    submission=sub, value="c")
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 0)

        # user responded - partially incorrectly
        Response.objects.create(question=question, submission=sub, value="a")
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 0)

        # user responded - partially incorrectly
        Response.objects.create(question=question, submission=sub, value="b")
        self.assertFalse(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 0)

        # kill the incorrect one
        c.delete()
        self.assertTrue(question.is_user_correct(self.user))
        self.assertEquals(self.quiz.score(self.user), 1)


class AnswerTest(TestCase):
    def test_str(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice")
        answer = Answer.objects.create(question=question, label="an answer")
        self.assertEqual(smart_str(answer), "an answer")

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
        answer = Answer.objects.create(question=question,
                                       label="an answer",
                                       css_extra='css-class')
        d = answer.as_dict()
        self.assertEqual(d['label'], 'an answer')
        self.assertFalse(d['correct'])
        self.assertEqual(d['css_extra'], 'css-class')

    def test_quiz_round_trip(self):
        quiz = Quiz.objects.create()
        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="single choice",
            css_extra="test-css-class"
        )
        Answer.objects.create(question=question, label="an answer")
        Answer.objects.create(
            question=question, label="another answer",
            explanation="an explanation", css_extra='css-class')

        d = quiz.as_dict()
        quiz2 = Quiz.objects.create()
        quiz2.import_from_dict(d)
        self.assertEqual(quiz2.question_set.count(), 1)
        q1 = quiz2.question_set.first()

        self.assertEqual(q1.css_extra, question.css_extra)

        # validate answer parameters
        a1 = q1.answer_set.get(label='an answer')
        self.assertEqual(a1.css_extra, '')
        self.assertEqual(a1.explanation, '')

        a2 = q1.answer_set.get(label='another answer')
        self.assertEqual(a2.css_extra, 'css-class')
        self.assertEqual(a2.explanation, 'an explanation')


class SubmissionTest(TestCase):
    def test_str(self):
        quiz = Quiz.objects.create()
        user = User.objects.create(username="testuser")
        s = Submission.objects.create(quiz=quiz, user=user)
        self.assertTrue(
            smart_str(s).startswith(
                "quiz %d submission by testuser" % quiz.id))


class ResponseTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create()
        self.question = Question.objects.create(
            quiz=self.quiz, text="foo", question_type="single choice")
        self.answer = Answer.objects.create(
            question=self.question,
            label="an answer")
        self.user = User.objects.create(username="testuser")
        self.submission = Submission.objects.create(
            quiz=self.quiz, user=self.user)

    def test_str(self):
        response = Response.objects.create(
            question=self.question,
            submission=self.submission,
            value=self.answer.label)
        self.assertTrue(smart_str(response).startswith("response to "))

    def test_is_correct(self):
        response = Response.objects.create(
            question=self.question,
            submission=self.submission,
            value=self.answer.label)
        self.assertFalse(response.is_correct())

    def test_answer(self):
        response = Response.objects.create(
            question=self.question,
            submission=self.submission,
            value=self.answer.label)
        self.assertEqual(response.answer(), self.answer)
