#coding=utf-8
from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.contrib.auth import get_user_model


STATUSES = (
    ('new', u'新建'),
    ('working', u'工作中'),
    ('resolved', u'解决完成'),
    ('reopen', u'重启'),
    ('closed', u'关闭'),
)


class Attached(models.Model):
    attached = models.FileField(u'附件', upload_to='task_tracker_upload')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey()

    class Meta:
        verbose_name = u'附件'
        verbose_name_plural = u'附件'


class Task(models.Model):
    title = models.CharField(u'标题', max_length=200)
    desc = models.TextField(u'详细描述', blank=True)
    status = models.CharField(u'状态', choices=STATUSES, max_length=10)
    created = models.DateTimeField(u'创建时间', default=now)
    modified = models.DateTimeField(u'修改时间', default=now)

    def __unicode__(self):
        return self.title


class Discussion(models.Model):
    task = models.ForeignKey(Task)
    discussion = models.TextField(u'讨论')
    created = models.DateTimeField(u'创建时间', default=now)
    modified = models.DateTimeField(u'修改时间', default=now)
    user = models.ForeignKey(get_user_model(), null=True, blank=True)

    class Meta:
        verbose_name = u'讨论'
        verbose_name_plural = u'讨论'
