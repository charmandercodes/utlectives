from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):

    course_completion = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-600 focus:ring-blue-600 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder:text-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500',
            'placeholder': '2025-AUTUMN',
            'pattern': r'\d{4}-(AUTUMN|SPRING|SUMMER|WINTER)',
            'title': 'Please enter in format: YYYY-SEASON (e.g., 2025-AUTUMN)'
        })
    )
    
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
                        
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }



