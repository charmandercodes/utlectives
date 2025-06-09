from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    enjoyment = models.FloatField(default=0.0)
    usefullness = models.FloatField(default=0.0)
    manageability = models.FloatField(default=0.0)
    overall_rating = models.FloatField(default=0.0)
    sessions = models.JSONField(default=list)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Review(models.Model):
    # required 
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    enjoyment = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    usefullness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    manageability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_date = models.DateTimeField(auto_now_add=True)
    course_completion = models.CharField(max_length=20)
    # not required 
    title = models.CharField(max_length=50, blank=True, null=True)
    text_review = models.TextField(blank=True, null=True)     
    grade = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Review of {self.course.code} by {self.author.username}"

