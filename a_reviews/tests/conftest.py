# tests/conftest.py
import pytest
from playwright.sync_api import Playwright
from a_reviews.factories import CourseFactory, ReviewFactory, UserFactory

# Playwright fixtures 
@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    browser = playwright.chromium.launch()
    yield browser
    browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

# General fixtures

@pytest.fixture
def courses():
    """Create a batch of courses"""
    return CourseFactory.create_batch(5)

@pytest.fixture
def user(db):
    """Create a test user"""
    return UserFactory()

@pytest.fixture
def user2(db):
    """Create a test user"""
    return UserFactory()

@pytest.fixture
def user3(db):
    """Create a test user"""
    return UserFactory()

@pytest.fixture
def other_user(db):
    """Create another test user for permission testing"""
    return UserFactory()

@pytest.fixture
def course(db):
    """Create one test course"""
    return CourseFactory()

@pytest.fixture
def review(db, user, course):
    """Create a test review"""
    return ReviewFactory(author=user, course=course)

@pytest.fixture
def reviews(db, user, courses):
    """Create multiple test reviews"""
    return [ReviewFactory(author=user, course=course) for course in courses]

@pytest.fixture
def course_with_two_reviews(db, course, user, other_user):
    """Create a course with 2 reviews by different users"""
    review1 = ReviewFactory(course=course, author=user)
    review2 = ReviewFactory(course=course, author=other_user)
    return course, [review1, review2]