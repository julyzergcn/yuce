# coding=utf-8
from django.contrib import admin
from django.utils.timezone import now
from django.contrib.contenttypes.generic import GenericStackedInline

from task_tracker.models import Task, Attached, Discussion


class DisscussionInline(admin.StackedInline):
    model = Discussion
    extra = 0
    fields = ('user', 'discussion', 'modified')
    readonly_fields = ('modified', )


class AttachedInline(GenericStackedInline):
    model = Attached
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'modified')
    ordering = ('-modified', )
    fields = ('title', 'desc', 'status', 'created', 'modified')
    readonly_fields = ('created', 'modified')
    inlines = (AttachedInline, DisscussionInline)

    def save_model(self, request, obj, form, change):
        if change:
            obj.modified = now()
        obj.save()


admin.site.register(Task, TaskAdmin)
