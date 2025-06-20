from django.db import models
from django.conf import settings
from projects.models import Project
from cards.models import Card, Column

class WorkItemType(models.Model):
    name = models.CharField(max_length=50)  # epic, bug, story, task

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class WorkItem(models.Model):
    type = models.ForeignKey(WorkItemType, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.IntegerField(null=True, blank=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_items')
    performer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_items')
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    board = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='tasks')
    tags = models.ManyToManyField(Tag, through='WorkItemTag', related_name='work_items')
    due_date = models.DateField(null=True, blank=True)
    attachments = models.ManyToManyField('Attachment', blank=True, related_name='work_items')

class WorkItemTag(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('work_item', 'tag')

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or self.file.name


class Comment(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class WorkItemHistory(models.Model):
    work_item = models.ForeignKey('WorkItem', on_delete=models.CASCADE, related_name='history')
    from_column = models.ForeignKey('cards.Column', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    to_column = models.ForeignKey('cards.Column', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.work_item.title}: {self.from_column} → {self.to_column} @ {self.moved_at}'
