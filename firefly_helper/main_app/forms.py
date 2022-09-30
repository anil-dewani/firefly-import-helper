from django import forms
from django.forms import ClearableFileInput
from main_app import models

class StatementFileForm(forms.ModelForm):
    class Meta:
        model = models.StatementFile
        fields = ['files']
        widgets = {
            'files': ClearableFileInput(attrs={
                'multiple': True,
            })
        }