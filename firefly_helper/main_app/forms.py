from django import forms
from django.forms import ClearableFileInput
from main_app import models

class StatementFileForm(forms.ModelForm):
    class Meta:
        model = models.StatementFile
        fields = ['statement_file']
        widgets = {
            'statement_file': ClearableFileInput(attrs={
                'multiple': True,
            })
        }


class AmazonStatementFileForm(forms.ModelForm):
    class Meta:
        model = models.AmazonStatementFile
        fields = ['statement_file']
        widgets = {
            'statement_file': ClearableFileInput(attrs={
                'multiple': True,
            }),
        }