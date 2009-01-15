from django.contrib import admin

from qs.queue.models import Queue, Message


class QueueAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_expire')
    ordering = ('name',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'visible', 'expires', 'queue')
    list_filter = ('visible',)
    raw_id_fields = ('queue',)


admin.site.register(Queue, QueueAdmin)
admin.site.register(Message, MessageAdmin)

