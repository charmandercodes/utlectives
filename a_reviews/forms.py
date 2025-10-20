from django import forms
from .models import Review
import datetime

class ReviewForm(forms.ModelForm):

        # Get current year and create a range
    current_year = datetime.datetime.now().year
    year_choices = [(year, str(year)) for year in range(current_year - 5, current_year + 2)]
    
    session_choices = [
        # Main semester sessions (90.6% of courses)
        ('SPRING', 'Spring'),
        ('AUTUMN', 'Autumn'),
        ('SUMMER', 'Summer'),
        ('OTHER', 'Other'),
    ]


    completion_year = forms.ChoiceField(
        choices=year_choices,
        initial=current_year,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-600 focus:ring-blue-600 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-blue-500 dark:focus:ring-blue-500'
        })
    )

    completion_session = forms.ChoiceField(
        choices=session_choices,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-600 focus:ring-blue-600 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-blue-500 dark:focus:ring-blue-500'
        })
    )
    

    class Meta:
        model = Review
        fields = [
            'title', 'text_review', 'overall_rating', 'enjoyment', 
            'usefullness', 'manageability', 'grade', 'is_anonymous'
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
                'maxlength': 100
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine year and session into the course_completion field
        year = self.cleaned_data['completion_year']
        session = self.cleaned_data['completion_session']
        instance.course_completion = f"{year}-{session}"
        
        if commit:
            instance.save()
        return instance



