from django import forms

class CodeEntryForm(forms.Form):
    code = forms.CharField(max_length=255, required=True, label='Enter Code')