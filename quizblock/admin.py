from models import Quiz, Question, Answer, Response, Submission
from django.contrib import admin
from django import forms

admin.site.register(Response)
admin.site.register(Submission)

class AnswerInlineForm(forms.ModelForm):
   class Meta:
        model = Answer
        widgets = { 
           'label': forms.Textarea(attrs={'rows': 1 }),
        }

class AnswerInlineAdmin(admin.TabularInline):
    form = AnswerInlineForm
    model = Answer
    extra = 0
    template = 'admin/quizblock/answer/edit_inline/tabular.html'
    widgets = { 
           'label': forms.Textarea(attrs={'rows': 1 }),
    }
    
    def change_view(self, request, object_id, extra_context=None):
        my_context = {
           'is_iframe': request.REQUEST.has_key('_iframe')
        }
        return super(AnswerInlineAdmin, self).change_view(request, object_id, extra_context=my_context)

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInlineAdmin, ]
    template = 'admin/quizblock/question/change_form.html'
    
    fieldsets = (
        (None, {
            'fields': ( )
        }),
        ('All Question Properties', {
            'classes': ('collapse',),
            'fields': ('question_type', 'intro_text', 'text', 'explanation')
        }),
    )
    
admin.site.register(Question, QuestionAdmin)
    
class QuestionModelForm(forms.ModelForm):
   class Meta:
        model = Question
        widgets = { 
           'text': forms.Textarea(attrs={'rows': 1 }),
           'explanation': forms.Textarea(attrs={'rows': 1 }),
           'intro_text': forms.Textarea(attrs={'rows': 1 }), 
        }
        
        fields = ('question_type', 'intro_text', 'text', 'explanation')
  
class QuestionInlineAdmin(admin.TabularInline):
    form = QuestionModelForm
    model = Question
    inlines = [ AnswerInlineAdmin, ]
    template = 'admin/quizblock/question/edit_inline/tabular.html'
    extra = 0
    
class QuizModelForm(forms.ModelForm):
   class Meta:
        model = Quiz
        widgets = { 
           'description': forms.Textarea(attrs={'rows': 3 })
        }
      
class QuizAdmin(admin.ModelAdmin):
    form = QuizModelForm
    model = Quiz
    inlines = [QuestionInlineAdmin, ]

admin.site.register(Quiz, QuizAdmin)


