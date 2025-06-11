from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'title', 'text_review', 'overall_rating', 'enjoyment', 
            'usefullness', 'manageability', 'grade', 'course_completion', 
            'is_anonymous'
        ]
        # Exclude course and author - these should be set in the view
        
        labels = {
            'title': 'Title',
            'text_review': 'Review',
            'overall_rating': 'Overall Rating',
            'enjoyment': 'Enjoyment',
            'usefullness': 'Usefulness',  # Note: you have a typo in your model field name
            'manageability': 'Manageability',
            'grade': 'Grade',
            'course_completion': 'Course Completion',
            'is_anonymous': 'Display as anonymous'
        }
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for your review',
                'maxlength': 50
            }),
            
            'text_review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your experience with this course...',
                'maxlength': 1000
            }),
            
            'overall_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                }
            ),
            
            'enjoyment': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                }
            ),
            
            'usefullness': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                }
            ),
            
            'manageability': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                }
            ),
            
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'placeholder': 'Enter your grade (0-100)',
                'step': 1
            }),
            
            'course_completion': forms.Select(
                choices=[
                    ('completed', 'Completed'),
                    ('in_progress', 'In Progress'),
                    ('dropped', 'Dropped'),
                    ('audited', 'Audited')
                ],
                attrs={
                    'class': 'form-select',
                }
            ),
            
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }



