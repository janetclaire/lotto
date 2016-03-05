from __future__ import unicode_literals
from django.shortcuts import render
from .forms import PunterForm, EntryForm, SigninForm
from .models import Punter, Draw, Entry
from django.views.generic import View, TemplateView, ListView
from django.http import HttpResponseRedirect

class LandingPage(View):
    '''Page directs user to either register or sign in'''
    fclass = SigninForm
    template = 'landing.html'

    def get(self, request):
        form = self.fclass(request.GET)
        if request.GET.get('email'):
             punter = Punter.objects.get(email=request.GET.get('email'))
             return HttpResponseRedirect('/entry/{}/'.format(punter.pk))
        return render(request, self.template, {'form': form, 'title':"Welcome to our Lotteries"})

class PunterView(View):
    '''Registration Form'''
    fclass = PunterForm
    template = 'punter.html'

    def get(self, request):
        form = self.fclass()
        return render(request, self.template, {'form':form, 'title':"Sign up to enter our Lotteries"})

    def post(self, request):
        form = self.fclass(data = request.POST)
        if form.is_valid(): 
             punter = form.save()
             return HttpResponseRedirect('/entry/{}/'.format(punter.pk))
        else: return render(request, self.template, {'form':form, 'title':"Sign up to enter our Lotteries"})

class EntryView(View):
    '''Form to make an entry in a draw'''
    fclass = EntryForm
    template = 'entry.html'

    def get(self, request, punterid):
        form = self.fclass(initial = {'punter': punterid})
        # restrict choice of draws to those that have not taken place, and which the punter has not already entered
        form.fields['draw'].queryset = Draw.objects.filter(db_winning_combo='').exclude(entry__punter__pk=punterid)
        punter = Punter.objects.get(pk=punterid)
        return render(request, self.template, {'form':form, 'punter': punter, 'title':"Enter the lottery"})

    def post(self, request, punterid):
        form = self.fclass(data = request.POST)
        # restrict choice of draws to those that have not taken place, and which the punter has not already entered
        form.fields['draw'].queryset = Draw.objects.filter(db_winning_combo='').exclude(entry__punter__pk=punterid)
        punter = Punter.objects.get(pk=punterid)
        if form.is_valid(): 
             entry = form.save()
             return HttpResponseRedirect('/goodluck/{}/{}/'.format(punterid, entry.pk))
        return render(request, self.template, {'form':form, 'punter': punter, 'title':"Enter the lottery"})

class EntriesView(ListView):
    template_name = "entries.html"

    def get_queryset(self):
        self.punter = Punter.objects.get(pk=self.kwargs['punterid'])
        return Entry.objects.filter(punter=self.punter)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EntriesView, self).get_context_data(**kwargs)
        context['punter'] = self.punter
        return context


class GoodluckView(TemplateView):
    '''Page to be shown after the user has entered a draw'''
    template_name = "goodluck.html"

    def get_context_data(self, **kwargs):
        context = super(GoodluckView, self).get_context_data(**kwargs)
        context['punter'] = Punter.objects.get(pk=context['punterid'])
        return context
