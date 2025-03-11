from django.db import models

# Create your models here.
class CategoryWiseResumesScore(models.Model):
    job_description=models.CharField(max_length=50)
    file_name=models.CharField(max_length=50)
    score=models.IntegerField()
