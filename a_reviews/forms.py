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
        
        # Sub-semester sessions (10.6% of courses)
        ('AUTUMN_B', 'Autumn B'),
        ('SPRING_B', 'Spring B'),
        ('SPRING_C', 'Spring C'),
        ('AUTUMN_C', 'Autumn C'),
        ('AUTUMN_D', 'Autumn D'),
        ('SPRING_D', 'Spring D'),
        
        # Research sessions (11.1% of courses)
        ('RESEARCH_1', 'Research 1'),
        ('RESEARCH_2', 'Research 2'),
        
        # Intensive/Block sessions (8.1% of courses)
        ('SESSION_1', 'Session 1'),
        ('SESSION_2', 'Session 2'),
        ('SESSION_3', 'Session 3'),
        ('SESSION_4', 'Session 4'),
        ('SESSION_5', 'Session 5'),
        ('SESSION_6', 'Session 6'),
        
        # Specific month sessions (6.6% of courses)
        ('JANUARY', 'January'),
        ('FEBRUARY', 'February'),
        ('MARCH', 'March'),
        ('APRIL', 'April'),
        ('MAY', 'May'),
        ('JUNE', 'June'),
        ('JULY', 'July'),
        ('AUGUST', 'August'),
        ('SEPTEMBER', 'September'),
        ('OCTOBER', 'October'),
        ('NOVEMBER', 'November'),
        ('DECEMBER', 'December'),
        
        # Multi-month sessions (1.2% of courses)
        ('JAN_MAR', 'January-March'),
        ('MAR_MAY', 'March-May'),
        ('MAY_JULY', 'May-July'),
        ('JULY_SEPT', 'July-September'),
        ('AUG_OCT', 'August-October'),
        ('OCT_DEC', 'October-December'),
        ('DEC_FEB', 'December-February'),
        
        # Special sessions
        ('CALENDAR_B_SPRING', 'Calendar B Spring'),
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine year and session into the course_completion field
        year = self.cleaned_data['completion_year']
        session = self.cleaned_data['completion_session']
        instance.course_completion = f"{year}-{session}"
        
        if commit:
            instance.save()
        return instance



