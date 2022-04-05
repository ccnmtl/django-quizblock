from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.encoding import smart_text
from pagetree.models import PageBlock
from pagetree.reports import ReportColumnInterface

from django.contrib.contenttypes.fields import GenericRelation


class Quiz(models.Model):
    pageblocks = GenericRelation(PageBlock)
    description = models.TextField(blank=True)
    rhetorical = models.BooleanField(default=False)
    allow_redo = models.BooleanField(default=True)
    show_submit_state = models.BooleanField(default=True)
    template_file = "quizblock/quizblock.html"

    display_name = "Quiz"
    exportable = True
    importable = True

    def pageblock(self):
        return self.pageblocks.first()

    def __str__(self):
        return smart_text(self.pageblock())

    def needs_submit(self):
        return not self.rhetorical

    def submit(self, user, data):
        """ a big open question here is whether we should
        be validating submitted answers here, on submission,
        or let them submit whatever garbage they want and only
        worry about it when we show the admins the results """
        s = Submission.objects.create(quiz=self, user=user)
        for k in data.keys():
            if k.startswith('question'):
                qid = int(k[len('question'):])
                question = Question.objects.get(id=qid)
                # it might make more sense to just accept a QueryDict
                # instead of a dict so we can use getlist()
                if isinstance(data[k], list):
                    for v in data[k]:
                        Response.objects.create(
                            submission=s,
                            question=question,
                            value=v)
                else:
                    Response.objects.create(
                        submission=s,
                        question=question,
                        value=data[k])

    def redirect_to_self_on_submit(self):
        return self.show_submit_state

    def unlocked(self, user):
        # meaning that the user can proceed *past* this one,
        # not that they can access this one. careful.

        if user.is_anonymous:
            return False

        return Submission.objects.filter(quiz=self, user=user).count() > 0

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea(),
                                          initial=self.description)
            rhetorical = forms.BooleanField(initial=self.rhetorical)
            allow_redo = forms.BooleanField(initial=self.allow_redo)
            show_submit_state = forms.BooleanField(
                initial=self.show_submit_state)
            alt_text = ("<a href=\"" + reverse("edit-quiz", args=[self.id])
                        + "\">manage questions/answers</a>")
        return EditForm()

    @classmethod
    def add_form(cls):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
            rhetorical = forms.BooleanField()
            allow_redo = forms.BooleanField()
            show_submit_state = forms.BooleanField(initial=True)
        return AddForm()

    @classmethod
    def create(cls, request):
        return cls.objects.create(
            description=request.POST.get('description', ''),
            rhetorical=request.POST.get('rhetorical', '') == 'on',
            allow_redo=request.POST.get('allow_redo', '') == 'on',
            show_submit_state=request.POST.get(
                'show_submit_state', '') == 'on')

    @classmethod
    def create_from_dict(cls, d):
        q = cls.objects.create(
            description=d.get('description', ''),
            rhetorical=d.get('rhetorical', False),
            allow_redo=d.get('allow_redo', True),
            show_submit_state=d.get('show_submit_state', True),
        )
        q.import_from_dict(d)
        return q

    def edit(self, vals, files):
        self.description = vals.get('description', '')
        self.rhetorical = vals.get('rhetorical', '') == 'on'
        self.allow_redo = vals.get('allow_redo', '') == 'on'
        self.show_submit_state = vals.get('show_submit_state', '') == 'on'
        self.save()

    def add_question_form(self, request=None):
        return QuestionForm(request)

    def update_questions_order(self, question_ids):
        self.set_question_order(question_ids)

    def clear_user_submissions(self, user):
        Submission.objects.filter(user=user, quiz=self).delete()

    def as_dict(self):
        d = dict(description=self.description,
                 rhetorical=self.rhetorical,
                 allow_redo=self.allow_redo,
                 show_submit_state=self.show_submit_state)
        d['questions'] = [q.as_dict() for q in self.question_set.all()]
        return d

    def import_from_dict(self, d):
        self.description = d.get('description', '')
        self.rhetorical = d.get('rhetorical', False)
        self.allow_redo = d.get('allow_redo', True)
        self.show_submit_state = d.get('show_submit_state', True)
        self.save()
        self.submission_set.all().delete()
        self.question_set.all().delete()
        for q in d.get('questions', []):
            question = Question.objects.create(
                quiz=self, text=q.get('text', ''),
                question_type=q.get('question_type', None),
                explanation=q.get('explanation', ''),
                intro_text=q.get('intro_text', ''),
                css_extra=q.get('css_extra', ''))
            for a in q.get('answers', []):
                x = Answer.objects.create(question=question,
                                          value=a.get('value', None),
                                          label=a.get('label', ''),
                                          correct=a.get('correct', False),
                                          css_extra=a.get('css_extra', ''))
                if 'explanation' in a:
                    x.explanation = a.get('explanation', '')
                    x.save()

    def summary_render(self):
        if len(self.description) < 61:
            return self.description
        else:
            return self.description[:61] + "..."

    def report_metadata(self):
        columns = []
        hierarchy = self.pageblock().section.hierarchy
        for q in self.question_set.all():
            if q.answerable():
                # one row for each question/answer for choice questions
                for a in q.answer_set.all():
                    columns.append(QuestionColumn(hierarchy=hierarchy,
                                                  question=q, answer=a))
            else:
                columns.append(QuestionColumn(hierarchy=hierarchy, question=q))
        return columns

    def report_values(self):
        columns = []
        hierarchy = self.pageblock().section.hierarchy
        for q in self.question_set.all():
            if q.is_multiple_choice():
                # need to make a column for each answer
                for a in q.answer_set.all():
                    columns.append(QuestionColumn(
                        hierarchy=hierarchy, question=q, answer=a))
            else:
                # single choice, short text and long text need only one row
                columns.append(QuestionColumn(hierarchy=hierarchy, question=q))
        return columns

    def score(self, user):
        '''
            returns
            - None if incomplete or has no questions
            - float score if complete
        '''
        if self.question_set.count() == 0:
            return None

        score = 0.0
        for question in self.question_set.all():
            correct = question.is_user_correct(user)
            if correct is None:
                return None
            elif correct:
                score += 1

        return score / self.question_set.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField(help_text='Required')
    question_type = models.CharField(
        max_length=256,
        choices=(
            ("multiple choice", "Multiple Choice: Multiple answers"),
            ("single choice", "Multiple Choice: Single answer"),
            ("single choice dropdown",
             "Multiple Choice: Single answer (dropdown)"),
            ("short text", "Short Text"),
            ("long text", "Long Text"),
        ))
    explanation = models.TextField(blank=True)
    intro_text = models.TextField(blank=True)
    css_extra = models.TextField(
        blank=True, null=True,
        help_text='extra CSS classes (space separated)')

    class Meta:
        order_with_respect_to = 'quiz'

    def __str__(self):
        return self.text

    def display_number(self):
        return self._order + 1

    def edit_form(self, request=None):
        return QuestionForm(request, instance=self)

    def add_answer_form(self, request=None):
        return AnswerForm(request)

    def correct_answer_values(self):
        return [a.value for a in self.answer_set.filter(correct=True)]

    def correct_answer_number(self):
        if self.question_type != "single choice":
            return None
        return self.answer_set.filter(correct=True).first()._order

    def correct_answer_letter(self):
        if (self.question_type != "single choice"
                or self.answer_set.count() == 0):
            return None
        return chr(ord('A') + self.correct_answer_number())

    def update_answers_order(self, answer_ids):
        self.set_answer_order(answer_ids)

    def answerable(self):
        """ whether it makes sense to have Answers associated with this """
        return self.question_type in ["multiple choice",
                                      "single choice",
                                      "single choice dropdown"]

    def is_short_text(self):
        return self.question_type == "short text"

    def is_long_text(self):
        return self.question_type == "long text"

    def is_single_choice(self):
        return self.question_type == "single choice"

    def is_single_choice_dropdown(self):
        return self.question_type == "single choice dropdown"

    def is_multiple_choice(self):
        return self.question_type == "multiple choice"

    def user_responses(self, user):
        qs = Submission.objects.filter(user=user,
                                       quiz=self.quiz).order_by("-submitted")
        if qs.count() == 0:
            return Response.objects.none()
        else:
            submission = qs.first()
            return Response.objects.filter(question=self,
                                           submission=submission)

    def as_dict(self):
        return dict(
            text=self.text,
            question_type=self.question_type,
            explanation=self.explanation,
            intro_text=self.intro_text,
            css_extra=self.css_extra,
            answers=[a.as_dict() for a in self.answer_set.all()]
        )

    def is_user_correct(self, user):
        '''
            * None if user has not responded
            * False if user has not answered or not answered correctly
            * True if user has responded and
                there is no correct answer or has answered correctly
        '''
        responses = self.user_responses(user)
        answers = self.correct_answer_values()

        if len(responses) == 0:
            return None  # incomplete

        if not self.answerable() or len(answers) == 0:
            return True  # a completed response is considered correct

        if len(answers) != len(responses):
            # The user hasn't completely answered the question yet
            return False

        correct = True
        for resp in responses:
            correct = correct and str(resp.value) in answers
        return correct


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)
    label = models.TextField(blank=True)
    correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    css_extra = models.CharField(
        max_length=256, blank=True,
        help_text='extra CSS classes (space separated)')

    class Meta:
        order_with_respect_to = 'question'

    def __str__(self):
        return self.label

    def display_number(self):
        return self._order + 1

    def edit_form(self, request=None):
        return AnswerForm(request, instance=self)

    def as_dict(self):
        return dict(value=self.value,
                    label=self.label,
                    correct=self.correct,
                    explanation=self.explanation,
                    css_extra=self.css_extra)


class Submission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "quiz %d submission by %s at %s" % (self.quiz.id,
                                                   smart_text(self.user),
                                                   self.submitted)


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    value = models.TextField(blank=True)

    class Meta:
        ordering = ('question',)

    def __str__(self):
        return "response to %s [%s]" % (smart_text(self.question),
                                        smart_text(self.submission))

    def is_correct(self):
        return self.value in self.question.correct_answer_values()

    def answer(self):
        """Returns the Answer associated with this Response.

        Not every Response has an Answer associated with it. This
        method is useful, for example, for single-choice quizzes.
        """
        return Answer.objects.filter(
            Q(question=self.question),
            Q(value=self.value) | Q(label=self.value)).first()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ("quiz",)
        fields = ('question_type', 'intro_text', 'text', 'explanation',
                  'css_extra')
        widgets = {
            'intro_text': forms.widgets.Textarea(attrs={'rows': 4}),
            'text': forms.widgets.Textarea(attrs={'rows': 4}),
            'explanation': forms.widgets.Textarea(attrs={'rows': 4}),
            'css_extra': forms.widgets.TextInput(),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ("question",)
        widgets = {
            'label': forms.widgets.Textarea(attrs={'rows': 4}),
            'explanation': forms.widgets.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        if 'value' not in self.cleaned_data:
            raise forms.ValidationError(
                'Please enter a meaningful value for this answer.')
        else:
            return self.cleaned_data


class QuestionColumn(ReportColumnInterface):

    def __init__(self, hierarchy, question, answer=None):
        self.hierarchy = hierarchy
        self.question = question
        self.answer = answer

        self._answer_cache = {}
        for a in self.question.answer_set.all():
            self._answer_cache[a.value] = a.id

    @classmethod
    def clean_header(cls, s):
        s = s.replace('<p>', '')
        s = s.replace('</p>', '')
        s = s.replace('</div>', '')
        s = s.replace('\n', '')
        s = s.replace('\r', '')
        s = s.replace('<', '')
        s = s.replace('>', '')
        s = s.replace('\'', '')
        s = s.replace('\"', '')
        s = s.replace(',', '')
        s = s.encode('utf-8')
        return s

    def question_id(self):
        return "%s_%s" % (self.hierarchy.id, self.question.id)

    def question_answer_id(self):
        return "%s_%s_%s" % (self.hierarchy.id,
                             self.question.id,
                             self.answer.id)

    def identifier(self):
        if self.question and self.answer:
            return self.question_answer_id()
        else:
            return self.question_id()

    def metadata(self):
        row = [self.hierarchy.name,
               self.question_id(),
               "Quiz",
               self.question.question_type,
               self.clean_header(self.question.text)]
        if self.answer:
            row.append(self.answer.id)
            row.append(self.clean_header(self.answer.label))
        return row

    def user_value(self, user):
        value = None
        submission = Submission.objects.filter(
            quiz=self.question.quiz, user=user).order_by("-submitted").first()
        if submission:
            value = ''
            responses = submission.response_set.filter(question=self.question)

            if responses.count() > 0:
                if self.question.is_single_choice():
                    # map the answer id to the answer value
                    first_value = responses.first().value
                    value = self._answer_cache[first_value]
                elif self.question.is_multiple_choice():
                    # did the user select the specified answer?
                    values = responses.values_list('value', flat=True)
                    if self.answer.value in values:
                        value = self.answer.id
                else:  # short or long text
                    value = responses.first().value

            value = smart_text(value)
        return value
