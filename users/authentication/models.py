from django.db import models


# Create your models here.
class EmailVerify(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)

    objects = models.Manager()

    def __str__(self):
        return f'{self.email} - {self.code}'
