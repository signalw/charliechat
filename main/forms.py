from django import forms

class UserInputForm(forms.Form):
    text_input = forms.CharField(min_length=1)