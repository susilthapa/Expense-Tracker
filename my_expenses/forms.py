from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Item

# from flatpickr import DatePickerInput, DateTimePickerInput


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email', help_text="Enter Valid Email Address")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('User with this email already exists!')
        return email


class DateInput(forms.DateInput):
    input_type = 'date'


class SearchHistoryForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['added_on']
        # widgets = {'added_on': DatePickerInput()}
        widgets = {'added_on': DateInput()}
