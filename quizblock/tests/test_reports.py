from pagetree.models import Hierarchy
from pagetree.reports import PagetreeReport
from quizblock.models import Quiz, Question, Answer, Submission, \
    QuestionColumn, Response
from pagetree.tests.factories import UserFactory, PagetreeTestCase


class QuestionColumnTest(PagetreeTestCase):

    def setUp(self):
        super(QuestionColumnTest, self).setUp()

        quiz = Quiz()
        quiz.save()

        self.section = self.hierarchy_one.get_root().get_next()
        self.section.append_pageblock('Quiz', '', content_object=quiz)

        self.user = UserFactory()
        self.user2 = UserFactory()

        self.single_answer = Question.objects.create(
            quiz=quiz, text='single answer', question_type='single choice')
        self.single_answer_one = Answer.objects.create(
            question=self.single_answer, label='Yes', value='1')
        self.single_answer_two = Answer.objects.create(
            question=self.single_answer, label='No', value='0')

        self.multiple_answer = Question.objects.create(
            quiz=quiz, text='multiple answer', question_type='multiple choice')
        self.multiple_answer_one = Answer.objects.create(
            question=self.multiple_answer, label='Yes', value='1')
        self.multiple_answer_two = Answer.objects.create(
            question=self.multiple_answer, label='No', value='0')

        self.short_text = Question.objects.create(
            quiz=quiz, text='short text', question_type='short text')

        self.long_text = Question.objects.create(
            quiz=quiz, text='long text', question_type='long text')

        self.submission = Submission.objects.create(quiz=quiz, user=self.user)

        self.report = PagetreeReport()

    def test_clean_header_empty(self):
        self.assertEqual(QuestionColumn.clean_header(''), '')

    def test_clean_header(self):
        self.assertEqual(QuestionColumn.clean_header('<<<<foo>>>>'), 'foo')

    def test_single_answer(self):
        Response.objects.create(submission=self.submission,
                                question=self.single_answer,
                                value='0')

        column = QuestionColumn(self.hierarchy_one, self.single_answer)

        # identifier
        identifier = '%s_%s' % (self.hierarchy_one.id, self.single_answer.id)
        self.assertEquals(column.identifier(), identifier)

        # key row
        key_row = ['one', identifier, 'Quiz', 'single choice', 'single answer']
        self.assertEquals(column.metadata(), key_row)

        # user value
        answer = self.single_answer.answer_set.get(value='0')
        self.assertEquals(column.user_value(self.user), str(answer.id))
        self.assertEquals(column.user_value(self.user2), None)

    def test_multiple_answer(self):
        Response.objects.create(submission=self.submission,
                                question=self.multiple_answer, value='0')
        Response.objects.create(submission=self.submission,
                                question=self.multiple_answer, value='1')

        a = self.multiple_answer.answer_set.get(value='1')
        column = QuestionColumn(self.hierarchy_one, self.multiple_answer, a)

        # identifier
        identifier = '%s_%s_%s' % (
            self.hierarchy_one.id, self.multiple_answer.id, a.id)
        self.assertEquals(column.identifier(), identifier)

        # key row
        identifier = '%s_%s' % (self.hierarchy_one.id, self.multiple_answer.id)
        key_row = ['one', identifier, 'Quiz', 'multiple choice',
                   'multiple answer', a.id, a.label]
        self.assertEquals(column.metadata(), key_row)

        # user value
        self.assertEquals(column.user_value(self.user), str(a.id))
        self.assertEquals(column.user_value(self.user2), None)

    def test_short_text(self):
        Response.objects.create(submission=self.submission,
                                question=self.short_text, value='yes')

        column = QuestionColumn(self.hierarchy_one, self.short_text)

        # identifier
        identifier = '%s_%s' % (self.hierarchy_one.id, self.short_text.id)
        self.assertEquals(column.identifier(), identifier)

        # key row
        key_row = ['one', identifier, 'Quiz', 'short text', 'short text']
        self.assertEquals(column.metadata(), key_row)

        # user value
        self.assertEquals(column.user_value(self.user), 'yes')
        self.assertEquals(column.user_value(self.user2), None)

    def test_long_text(self):
        Response.objects.create(submission=self.submission,
                                question=self.long_text,
                                value='a longer response')

        column = QuestionColumn(self.hierarchy_one, self.long_text)

        # identifier
        identifier = '%s_%s' % (self.hierarchy_one.id, self.long_text.id)
        self.assertEquals(column.identifier(), identifier)

        # key row
        key_row = ['one', identifier, 'Quiz', 'long text', 'long text']
        self.assertEquals(column.metadata(), key_row)

        # user value
        self.assertEquals(column.user_value(self.user), 'a longer response')
        self.assertEquals(column.user_value(self.user2), None)

    def test_report_metadata_columns(self):
        hierarchies = Hierarchy.objects.filter(name="one")
        columns = self.report.metadata_columns(hierarchies)
        self.assertEquals(len(columns), 7)

        self.assertEquals(columns[0].question, self.single_answer)
        self.assertEquals(columns[0].answer, self.single_answer_one)

        self.assertEquals(columns[1].question, self.single_answer)
        self.assertEquals(columns[1].answer, self.single_answer_two)

        self.assertEquals(columns[2].question, self.multiple_answer)
        self.assertEquals(columns[2].answer, self.multiple_answer_one)

        self.assertEquals(columns[3].question, self.multiple_answer)
        self.assertEquals(columns[3].answer, self.multiple_answer_two)

        self.assertEquals(columns[4].question, self.short_text)

        self.assertEquals(columns[5].question, self.long_text)

    def test_report_value_columns(self):
        hierarchies = Hierarchy.objects.filter(name="one")
        columns = self.report.value_columns(hierarchies)
        self.assertEquals(len(columns), 6)

        self.assertEquals(columns[0].question, self.single_answer)
        self.assertIsNone(columns[0].answer)

        self.assertEquals(columns[1].question, self.multiple_answer)
        self.assertEquals(columns[1].answer, self.multiple_answer_one)

        self.assertEquals(columns[2].question, self.multiple_answer)
        self.assertEquals(columns[2].answer, self.multiple_answer_two)

        self.assertEquals(columns[3].question, self.short_text)

        self.assertEquals(columns[4].question, self.long_text)
