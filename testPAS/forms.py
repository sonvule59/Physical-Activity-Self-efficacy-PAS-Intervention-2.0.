from django import forms

class CodeEntryForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )