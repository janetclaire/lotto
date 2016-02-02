from django.contrib import admin

from .models import *

admin.site.register(LotteryType)
admin.site.register(Lottery)
admin.site.register(Punter)
admin.site.register(Entry)
admin.site.register(Win)
