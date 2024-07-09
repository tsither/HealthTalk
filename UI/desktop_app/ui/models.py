from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    # other fields also can be added
    class Meta:
        db_table = 'User'

    def __str__(self):
        return self.username
