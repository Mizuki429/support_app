from django.db import models

class Concern(models.Model):
    concern_text = models.TextField()
    ai_suggestion = models.TextField()
    scene_detail = models.TextField(blank=True, null=True)
    strategy = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
