from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    birth_date = models.IntegerField()
    # email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    class Meta:
        db_table = 'USER'

    def __str__(self):
        return self.first_name + ' ' + self.last_name
