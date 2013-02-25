from django import template
from quizblock.models import Response, Submission

register = template.Library()


class GetQuestionResponseNode(template.Node):
    def __init__(self, question, var_name):
        self.question = question
        self.var_name = var_name

    def render(self, context):
        q = context[self.question]
        u = context['request'].user
        quiz = q.quiz
        r = Submission.objects.filter(quiz=quiz, user=u).order_by("-submitted")
        if r.count() == 0:
            return ''
        submission = r[0]
        r = Response.objects.filter(question=q, submission=submission)
        if r.count() > 0:
            context[self.var_name] = r[0]
        else:
            context[self.var_name] = None
        return ''


@register.tag('getquestionresponse')
def getquestionresponse(parser, token):
    question = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetQuestionResponseNode(question, var_name)


class IfAnswerInNode(template.Node):
    def __init__(self, response, answer, nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.response = response
        self.answer = answer

    def render(self, context):
        r = context[self.response]
        q = r.question
        a = context[self.answer]
        u = context['request'].user
        if a.value in [resp.value for resp in q.user_responses(u)]:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag('ifanswerin')
def ifanswerin(parser, token):
    response = token.split_contents()[1:][0]
    answer = token.split_contents()[1:][1]
    nodelist_true = parser.parse(('else', 'endifanswerin'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifanswerin',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return IfAnswerInNode(response, answer, nodelist_true, nodelist_false)
