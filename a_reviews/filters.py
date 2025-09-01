import django_filters
from django import forms
from a_reviews.models import Course, Review


class CourseFilter(django_filters.FilterSet):
    # Search filter
    search = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search courses...',
            'class': 'flex-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all'
        })
    )
    
    # Faculty filter (multiple choice)
    faculty = django_filters.MultipleChoiceFilter(
        choices=[
            ('analytics', 'Analytics'),
            ('business', 'Business'),
            ('Engineering and Information Technology', 'FEIT'),
            ('Law', 'Law'),
            ('health', 'Health'),
            ('science', 'Science'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox checkbox-primary checkbox-sm'
        })
    )
    

    
    # Session filter (custom method since sessions is JSONField)
    session = django_filters.MultipleChoiceFilter(
        choices=[
            ('Autumn', 'Autumn'),
            ('Spring', 'Spring'),
            ('Summer', 'Summer'),
            ('July', 'July'),
            ('Unavailable', 'Unavailable'),
        ],
        method='filter_by_sessions',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox checkbox-primary checkbox-sm'
        })
    )
    
    # Sorting field
    sort = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('overall_rating', 'overall_rating'),
            ('enjoyment', 'enjoyment'),
            ('usefullness', 'usefullness'),
            ('manageability', 'manageability'),
        ),
        field_labels={
            'name': 'Alphabetical (A-Z)',
            '-name': 'Alphabetical (Z-A)',
            '-overall_rating': 'Overall Rating',
            '-enjoyment': 'Enjoyability',
            '-usefullness': 'Usefulness',
            '-manageability': 'Manageability',
        }
    )

    class Meta:
        model = Course
        fields = ['search', 'faculty', 'session', 'sort']



    def filter_by_sessions(self, queryset, name, value):
        """Custom filter method for JSONField sessions"""
        if not value:
            return queryset
        
        # Filter courses that have any of the selected sessions
        course_ids = []
        for course in queryset:
            if any(session in course.sessions for session in value):
                course_ids.append(course.id)
        
        return queryset.filter(id__in=course_ids)
    

class ReviewFilter(django_filters.FilterSet):
    sort = django_filters.OrderingFilter(
        fields=(
            ('review_date', 'review_date'),
            ('course_completion', 'course_completion'),
            ('overall_rating', 'overall_rating'),
        ),
        field_labels={
            '-review_date': 'Most Recent',
            '-course_completion': 'Most Recently Taken',
            '-overall_rating': 'Highest Rating',
            'overall_rating': 'Lowest Rating',
        }
    )

    class Meta:
        model = Review
        fields = ['sort']