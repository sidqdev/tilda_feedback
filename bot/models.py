from django.db import models
from datetime import datetime


class Feedback(models.Model):
    name = models.TextField()
    working_place = models.TextField()
    text = models.TextField()
    media = models.FileField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    
    is_accepted = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.name}, {self.working_place}, {self.created_at}'