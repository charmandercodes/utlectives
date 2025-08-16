import pytest
from decimal import Decimal
from a_reviews.models import Course, Review
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestCourseModel:
    
    def test_str_representation(self):
        """Test the string representation of Course"""
        course = Course(code="CS101", name="Intro to Programming")
        assert str(course) == "CS101 - Intro to Programming"
    
    def test_total_reviews_property_no_reviews(self, course):
        """Test total_reviews property when course has no reviews"""
        assert course.total_reviews == 0
        
    def test_total_reviews_property_with_reviews(self, course_with_two_reviews):
        """Test total_reviews property when course has reviews"""
        course, reviews = course_with_two_reviews
        assert course.total_reviews == 2
    
    def test_update_ratings_no_reviews(self, course):
        """Test update_ratings method when course has no reviews"""

        course = course

        course.update_ratings()
        course.refresh_from_db()
        
        assert course.enjoyment == 0.0
        assert course.usefullness == 0.0
        assert course.manageability == 0.0
        assert course.overall_rating == 0.0
        assert course.review_count == 0
    
    def test_update_ratings_with_reviews(self, course, user, user2):
        """Test update_ratings method with multiple reviews"""
        # Create reviews with known values
        Review.objects.create(
            course=course, author=user,
            overall_rating=4, enjoyment=4, usefullness=5, manageability=3,
            course_completion="2024-Autumn"
        )

        Review.objects.create(
            course=course, author=user2,
            overall_rating=3, enjoyment=2, usefullness=3, manageability=5,
            course_completion="2024-Spring"
        )
        
        course.update_ratings()
        course.refresh_from_db()
        
        # Expected averages: 
        # overall: (4+3)/2=3.5, enjoyment: (4+2)/2=3.0
        # usefullness: (5+3)/2=4.0, manageability: (3+5)/2=4.0
        assert course.overall_rating == 3.5
        assert course.enjoyment == 3.0
        assert course.usefullness == 4.0
        assert course.manageability == 4.0

        assert course.review_count == 2
    
    def test_update_ratings_rounding(self, course, user, user2, user3):
        """Test that ratings are properly rounded to 1 decimal place"""
        
        # Create reviews that will need rounding
        Review.objects.create(
            course=course, author=user,
            overall_rating=4, enjoyment=4, usefullness=4, manageability=2,
            course_completion="2024-Autumn"
        )
        Review.objects.create(
            course=course, author=user2,
            overall_rating=3, enjoyment=3, usefullness=3, manageability=2,
            course_completion="2024-Spring"
        )
        Review.objects.create(
            course=course, author=user3,
            overall_rating=5, enjoyment=5, usefullness=4, manageability=2,
            course_completion="2024-Summer"
        )
        
        course.update_ratings()
        course.refresh_from_db()
        
        # Expected averages: (4+3+5)/3=4.0, (4+3+5)/3=4.0, (4+3+4)/3=3.666..., (2+2+2)/3=2.0
        assert course.overall_rating == 4.0
        assert course.enjoyment == 4.0
        assert course.usefullness == 3.7  # 3.666... rounded to 1 decimal
        assert course.manageability == 2.0

        assert course.review_count == 3
    
    def test_update_ratings_resets_to_zero_when_reviews_deleted(self, course_with_two_reviews):
        """Test that ratings reset to zero when all reviews are deleted"""
        course, reviews = course_with_two_reviews
        
        # First verify the course has ratings
        course.update_ratings()
        assert course.review_count == 2
        assert course.overall_rating > 0
        
        # Delete all reviews for this course
        course.review_set.all().delete()
        
        # Update ratings and verify they reset to zero
        course.update_ratings()
        course.refresh_from_db()
        
        assert course.enjoyment == 0.0
        assert course.usefullness == 0.0
        assert course.manageability == 0.0
        assert course.overall_rating == 0.0
        assert course.review_count == 0
    
    def test_update_ratings_single_review(self, course, user):
        """Test update_ratings with a single review"""
        Review.objects.create(
            course=course, author=user,
            overall_rating=5, enjoyment=4, usefullness=3, manageability=2,
            course_completion="2024-Autumn"
        )
        
        course.update_ratings()
        course.refresh_from_db()
        
        # With single review, averages should equal the review values
        assert course.overall_rating == 5.0
        assert course.enjoyment == 4.0
        assert course.usefullness == 3.0
        assert course.manageability == 2.0
        assert course.review_count == 1
    
    def test_default_field_values(self):
        """Test that default values are set correctly"""
        
        # used custom values here because factory defaults are not used in this test

        course = Course.objects.create(
            code="TEST001",
            name="Test Course",
            description="Test description"
        )
    
        
        assert course.enjoyment == 0.0
        assert course.usefullness == 0.0
        assert course.manageability == 0.0
        assert course.overall_rating == 0.0
        assert course.review_count == 0
        assert course.sessions == []
        assert course.page_reference is None
        assert course.faculty is None
    
    def test_default_course_ordering(self):
        """Test that courses are ordered correctly by overall_rating, review_count"""
        # Create courses with different ratings and review counts
        course1 = Course.objects.create(
            code="CS101", name="Course 1", description="Desc 1",
            overall_rating=4.0, review_count=10
        )
        course2 = Course.objects.create(
            code="CS102", name="Course 2", description="Desc 2",
            overall_rating=4.5, review_count=5
        )
        course3 = Course.objects.create(
            code="CS103", name="Course 3", description="Desc 3",
            overall_rating=4.5, review_count=15
        )
        
        courses = list(Course.objects.all())
        
        # Test the ordering principles
        assert courses[0].overall_rating == 4.5 and courses[0].review_count == 15  # Highest rating + count
        assert courses[1].overall_rating == 4.5 and courses[1].review_count == 5   # Same rating, lower count
        assert courses[2].overall_rating == 4.0 and courses[2].review_count == 10  # Lower rating, lower count
    
    @pytest.mark.parametrize("rating_values,expected_averages", [
        # Test case 1: All same values
        ([(5, 5, 5, 5), (5, 5, 5, 5)], (5.0, 5.0, 5.0, 5.0)),
        # Test case 2: All different values
        ([(1, 2, 3, 4), (5, 4, 3, 2)], (3.0, 3.0, 3.0, 3.0)),
        # Test case 3: Values that need rounding
        ([(4, 4, 4, 4), (5, 5, 5, 5), (3, 3, 3, 3)], (4.0, 4.0, 4.0, 4.0)),
    ])

    def test_update_ratings_parameterized(self, course, rating_values, expected_averages):
        """Parameterized test for different rating scenarios"""
        
        # Create reviews based on rating_values
        for i, (overall, enjoyment, usefullness, manageability) in enumerate(rating_values):
            user = User.objects.create_user(username=f"user{i}", password="pass")
            Review.objects.create(
                course=course, author=user,
                overall_rating=overall, enjoyment=enjoyment,
                usefullness=usefullness, manageability=manageability,
                course_completion="2024-Autumn"
            )
        
        course.update_ratings()
        course.refresh_from_db()
        
        expected_overall, expected_enjoyment, expected_usefullness, expected_manageability = expected_averages
        
        assert course.overall_rating == expected_overall
        assert course.enjoyment == expected_enjoyment
        assert course.usefullness == expected_usefullness
        assert course.manageability == expected_manageability
        assert course.review_count == len(rating_values)