from models import Quiz, Question, Answer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView


class EditQuizView(DetailView):
    model = Quiz


class DeleteQuestionView(DeleteView):
    model = Question

    def get_success_url(self):
        questionnaire = self.object.quiz
        return reverse("edit-quiz", args=[quiz.id])


class DeleteAnswerView(DeleteView):
    model = Answer

    def get_success_url(self):
        question = self.object.question
        return reverse("edit-question", args=[question.id])


class ReorderAnswersView(View):
    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        keys = [k for k in request.GET.keys() if k.startswith("answer_")]
        keys.sort(key=lambda x: int(x.split("_")[1]))
        answers = [int(request.GET[k])
                   for k in keys if k.startswith('answer_')]
        question.update_answers_order(answers)
        return HttpResponse("ok")


class ReorderQuestionsView(View):
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        keys = request.GET.keys()
        question_keys = [int(k[len('question_'):]) for k in keys
                         if k.startswith('question_')]
        question_keys.sort()
        questions = [int(request.GET['question_' + str(k)])
                     for k in question_keys]
        quiz.update_questions_order(questions)
        return HttpResponse("ok")


def add_question_to_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    form = quiz.add_question_form(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.save()
    return HttpResponseRedirect(reverse("edit-quiz", args=[quiz.id]))


def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = question.edit_form(request.POST)
        question = form.save(commit=False)
        question.save()
        return HttpResponseRedirect(reverse("edit-question",
                                            args=[question.id]))
    return render(
        request,
        'quizblock/edit_question.html',
        dict(question=question, answer_form=question.add_answer_form()))


def add_answer_to_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = question.add_answer_form(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            if answer.label == '':
                answer.label = answer.value
            answer.save()
            return HttpResponseRedirect(reverse("edit-question",
                                                args=[question.id]))
    else:
        form = question.add_answer_form()
    return render(
        request,
        'quizblock/edit_question.html',
        dict(question=question, answer_form=form))


def edit_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    form = answer.edit_form(request.POST)
    if request.method == "POST":
        if form.is_valid():
            answer = form.save(commit=False)
            answer.save()
            return HttpResponseRedirect(reverse("edit-answer",
                                                args=[answer.id]))
    else:
        form = answer.edit_form()
    return render(
        request,
        'quizblock/edit_answer.html',
        dict(answer_form=form, answer=answer))
