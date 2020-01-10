from django.contrib import admin

from .models import Source,Object,Info,Link


class InfoInline(admin.StackedInline):
    model = Info
    extra = 1

class LinkInlineFrom(admin.StackedInline):
    model = Link
    fk_name = 'o0'
    extra = 0

class LinkInlineTo(admin.StackedInline):
    model = Link
    fk_name = 'o1'
    extra = 0

class ObjectAdmin(admin.ModelAdmin):
    inlines = [
        LinkInlineFrom,LinkInlineTo, InfoInline,
    ]
    search_fields = ('name', 'otype', )

# Register your models here.
admin.site.register(Source)
admin.site.register(Object,ObjectAdmin)
