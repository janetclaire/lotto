from django.contrib import admin
from django.http import HttpResponseRedirect
from django.db.models import ObjectDoesNotExist

from .models import *

class WinInline(admin.StackedInline):
    model = Win
    extra = 0
    verbose_name_plural = "Win"
    def has_delete_permission(self, request, obj=None): return False
    readonly_fields = 'wintype', 'prize'

class DrawListFilter(admin.SimpleListFilter):
    '''Filters the list of draws according to whether or not the draw has already taken place'''
    title = 'result'
    parameter_name = 'result'
    def lookups(self, request, model_admin): return ( ('drawmade', 'draw made'), ('nodraw', 'draw not made yet'),)
    def queryset(self, request, queryset):
        if self.value() == 'drawmade': return queryset.filter(_winning_combo__isnull=False)
        if self.value() == 'nodraw': return queryset.filter(_winning_combo__isnull=True)

class EntryListFilter(admin.SimpleListFilter):
    '''Filters the list of entries by whether or not they won a prize'''
    title = 'result'
    parameter_name = 'result'
    def lookups(self, request, model_admin): return ( ('won', 'won'), ('lost', 'lost'),)
    def queryset(self, request, queryset):
        if self.value() == 'won': return queryset.filter(win__isnull=False)
        if self.value() == 'lost': return queryset.filter(win__isnull=True)

class EntryAdmin(admin.ModelAdmin):
    fields = 'draw', 'punter', '_entry'
    inlines = WinInline,
    list_filter = 'draw__lotterytype', ('draw__drawdate', admin.AllValuesFieldListFilter), 'punter', EntryListFilter
    list_display = 'draw', 'punter', 'won'

class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0
    def result(self, instance): 
        try: return 'won' if instance.win else 'lost'
        except ObjectDoesNotExist: return 'lost'
    def prize(self, instance):
        try: return instance.win.prize
        except ObjectDoesNotExist: return None
    readonly_fields = 'result', 'prize', 
    def has_delete_persission(self, request, obj=None): return False

class DrawAdmin(admin.ModelAdmin):
    fields = 'prize', '_winning_combo', 'drawdate', 'lotterytype'
    inlines = EntryInline, #WinTable
    list_filter = 'lotterytype', ('drawdate', admin.AllValuesFieldListFilter), DrawListFilter
    list_display = 'lotterytype', 'drawdate', '_winning_combo'

class PunterListFilter(admin.SimpleListFilter):
    '''Filters the list of punters by whether or not they have won a prize'''
    title = 'having won any lottery'
    parameter_name = 'result'
    def lookups(self, request, model_admin): return ( ('haswon', 'has won'), ('notwon', 'not won yet'),)
    def queryset(self, request, queryset):
        if self.value() == 'haswon': return queryset.filter(entry__win__isnull=False).distinct()
        if self.value() == 'notwon': return queryset.exclude(entry__win__isnull=False).distinct()

class PunterListFilterWin(admin.SimpleListFilter):
    '''Filters the list of punters to return only those who won a prize in a particular draw'''
    title = 'winners of specified lottery'
    parameter_name = 'draw'
    def lookups(self, request, model_admin): 
        return [(d.id, str(d)) for d in Draw.objects.all()]
    def queryset(self, request, queryset):
        draw = self.value()
        if draw: return queryset.filter(entry__draw=draw, entry__win__isnull=False)
        else: return queryset

class PunterAdmin(admin.ModelAdmin):
    list_filter = PunterListFilter, PunterListFilterWin
    list_display = 'name', 'address', 'email'

admin.site.register(MoreComplexLottery)
admin.site.register(SimpleLottery)
admin.site.register(Draw, DrawAdmin)
admin.site.register(Punter, PunterAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Win)

def allocateDraw(request, draw):
    '''Takes the winning combination from the admin/lotto/draw/change form and uses it to determine the winners of the draw,
       and allocate the prizes'''
    d = Draw.objects.get(id=draw)
    d.makeDraw(*[int(i) for i in request.POST.get('_winning_combo').split(',')])
    return HttpResponseRedirect('/admin/lotto/draw/{}/change/'.format(draw))
