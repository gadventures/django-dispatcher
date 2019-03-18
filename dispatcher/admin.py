import datetime

from django.contrib import admin
from django.db import connections

from .models import Chain, ChainResource, ChainEvent

TODAY = datetime.datetime.utcnow()
TOMORROW = TODAY + datetime.timedelta(days=1)


class DateNextUpdateFilter(admin.SimpleListFilter):

    title = 'Next Update'
    parameter_name = 'date_next_update'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples. The first element in each tuple is the coded
        value for the option that will appear in the URL query. The second
        element is the human readable option.
        """
        return (
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow And Beyond'),
        )

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value provided by the query
        string
        """
        if self.value() == 'today':
            return queryset.filter(date_next_update__gt=TODAY).filter(date_next_update__lt=TOMORROW)
        elif self.value() == 'tomorrow':
            return queryset.filter(date_next_update__gte=TOMORROW)


class ChainResourceInline(admin.TabularInline):
    model = ChainResource
    fields = ('resource_type', 'resource_id', )
    extra = 0


class ChainEventInLine(admin.TabularInline):
    model = ChainEvent
    fields = ('action', 'value', 'date_created', 'requested_by')
    readonly_fields = ('date_created', )
    extra = 0

class ChainAdmin(admin.ModelAdmin):
    list_display = ('state', 'chain_type', 'disabled', 'date_created', 'date_modified', 'date_next_update')
    list_filter = (DateNextUpdateFilter, 'chain_type', 'state')
    ordering = ('date_modified', )

    search_fields = ['messagechainitem__resource_id']

    inlines = [
        ChainResourceInline,
        ChainEventInLine,
    ]


admin.site.register(Chain, ChainAdmin)
