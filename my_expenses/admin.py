from django.contrib import admin
from .models import Item

admin.site.site_header = 'Expense Tracker Admin'


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'added_on', 'price')
    list_filter = ('user',)


admin.site.register(Item, ItemAdmin)