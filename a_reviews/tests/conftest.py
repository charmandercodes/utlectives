import pytest
from a_reviews.factories import CourseFactory, ReviewFactory, UserFactory

@pytest.fixture
def courses():
    return CourseFactory.create_batch(5)


@pytest.fixture
def user(db):
    """Create a test user"""
    return UserFactory()


@pytest.fixture
def other_user(db):
    """Create another test user for permission testing"""
    return UserFactory()


@pytest.fixture
def course(db):
    """Create a test course"""
    return CourseFactory()


@pytest.fixture
def review(db, user, course):
    """Create a test review"""
    return ReviewFactory(author=user, course=course)


@pytest.fixture
def reviews(db, user, courses):
    """Create multiple test reviews"""
    return [ReviewFactory(author=user, course=course) for course in courses]