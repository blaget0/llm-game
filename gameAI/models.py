from django.db import models

# Create your models here.
from django.db import models


class Drawing(models.Model):
    title = models.CharField(max_length=100)
    image_data = models.TextField()  # Будем хранить данные в формате base64
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title
    


from django.db import models
from django.contrib.auth.models import User

class GameResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wave = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Wave {self.wave}"