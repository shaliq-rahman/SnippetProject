from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Tag(models.Model):
    title = models.TextField(max_length=255, null=False, blank=False, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
      return "{}".format(self.title)
    
    
class TextSnippets(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, related_name="user_snippets", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, related_name="tag_snippets", on_delete=models.CASCADE)
    content =  models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
      return "{}".format(self.content)