from django import forms
from django.contrib.auth.models import User
from .models import Participant
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    registration_code = forms.CharField(max_length=10, required=True, label="Registration Code")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_registration_code(self):
        code = self.cleaned_data.get('registration_code')
        if code.lower() != 'wavepa':
            raise forms.ValidationError("Invalid registration code.")
        return code
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].lower()
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user
class InterestForm(forms.Form):
    interested = forms.ChoiceField(
        choices=[('yes', 'Interested'), ('no', 'Not Interested')],
        widget=forms.RadioSelect,
        required=True,
        label="Are you interested in determining your eligibility?"
    )
    reason = forms.CharField(
        max_length=255,
        required=False,
        label="If not interested, please provide a brief reason",
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 40})
    )

    def clean(self):
        cleaned_data = super().clean()
        interested = cleaned_data.get('interested')
        reason = cleaned_data.get('reason')
        if interested == 'no' and not reason:
            raise forms.ValidationError("Please provide a reason if you are not interested.")
        return cleaned_data

class CodeEntryForm(forms.Form):
    code = forms.CharField(label='Enter Code', max_length=100)

# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     confirm_password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

#     def clean_confirm_password(self):
#         password = self.cleaned_data.get('password')
#         confirm_password = self.cleaned_data.get('confirm_password')
#         if password and confirm_password and password != confirm_password:
#             raise forms.ValidationError("Passwords do not match")
#         return confirm_password

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ConsentForm(forms.Form):
    consent = forms.BooleanField(label="I consent to participate in this study", required=True)