from django import forms
from .models import *

class SignupForm(forms.Form):
    """docstring for SignupForm"""

    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    username = forms.CharField(label='Username', max_length=20)
    password1 = forms.CharField(label='Password', max_length=100)
    password2 = forms.CharField(label='Confirm Password', max_length=100)
    categories = forms.ChoiceField(choices=Category.get_categories())

    def clean_password2(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            raise forms.ValidationError("Password and Confirm Password Do Not Match.")
        return self.cleaned_data['password2']
    