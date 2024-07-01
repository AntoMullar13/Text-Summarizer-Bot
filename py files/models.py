from django.db import models
from django.contrib.auth.models import User

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.message} - {self.response}"
    