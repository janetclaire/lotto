from django.forms import ModelForm
from .models import *

class PunterForm(ModelForm):
    class Meta:
        model = Punter
        exclude = []

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = []

class SigninForm(ModelForm):
    class Meta:
        model = Punter
        fields = 'email',


