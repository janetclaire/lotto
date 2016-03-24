from django.forms import ModelForm
from django.forms.widgets import PasswordInput
from .models import *

class PunterForm(ModelForm):
    class Meta:
        model = Punter
        widgets = {'password': PasswordInput}
        exclude = []

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = []

class SigninForm(ModelForm):
    class Meta:
        model = Punter
        fields = 'email', 'password',
        labels = {'email': 'Existing Members Signin here with your email address', 'password': 'Password'}
        widgets = {'password': PasswordInput}


