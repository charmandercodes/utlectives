from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Case, When, IntegerField

# Create your models here.

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    enjoyment = models.FloatField(default=0.0)
    usefullness = models.FloatField(default=0.0)
    manageability = models.FloatField(default=0.0)
    overall_rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)  # Add this line
    sessions = models.JSONField(default=list)
    page_reference = models.URLField(max_length=200, blank=True, null=True)
    faculty = models.CharField(max_length=50, blank=True, null=True)
    has_sessions = models.BooleanField(default=False, db_index=True)
    LEVEL_CHOICES = [
    ('UG', 'Undergraduate'),
    ('PG', 'Postgraduate'),
    ]
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='UG', db_index=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def total_reviews(self):
        return self.review_set.count()
    
    def update_ratings(self):
        """Update cached rating averages and review count"""
        from django.db.models import Avg
        
        reviews = self.review_set.all()
        review_count = reviews.count()
        
        if reviews.exists():
            averages = reviews.aggregate(
                avg_enjoyment=Avg('enjoyment'),
                avg_usefullness=Avg('usefullness'),
                avg_manageability=Avg('manageability'),
                avg_overall=Avg('overall_rating')
            )
            
            self.enjoyment = round(averages['avg_enjoyment'] or 0, 1)
            self.usefullness = round(averages['avg_usefullness'] or 0, 1)
            self.manageability = round(averages['avg_manageability'] or 0, 1)
            self.overall_rating = round(averages['avg_overall'] or 0, 1)
        else:
            self.enjoyment = 0.0
            self.usefullness = 0.0
            self.manageability = 0.0
            self.overall_rating = 0.0
        
        self.review_count = review_count  # Update the cached count
        
        self.save(update_fields=[
            'enjoyment', 'usefullness', 'manageability', 
            'overall_rating', 'review_count'
        ])

    class Meta:
        ordering = [
            Case(
                When(level='UG', then=1),
                When(level='PG', then=2),
                output_field=IntegerField(),
            ),
            '-has_sessions', 
            '-overall_rating', 
            '-review_count'
            ]

    




class Review(models.Model):
    # required 
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    enjoyment = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    usefullness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    manageability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_date = models.DateTimeField(auto_now_add=True)
    course_completion = models.CharField(max_length=20, help_text="Format: YYYY-Season (e.g., 2025-Autumn)")
    
    # not required 
    title = models.CharField(max_length=50, blank=True, null=True)
    text_review = models.TextField(blank=True, null=True)     
    grade = models.IntegerField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review of {self.course.code} by {self.author.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course.update_ratings()  
    
    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        course.update_ratings()  
    
    class Meta:
        unique_together = ['course', 'author']

