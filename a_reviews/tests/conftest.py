import pytest
from a_reviews.factories import CourseFactory, ReviewFactory, UserFactory


@pytest.fixture
def courses():
    return CourseFactory.create_batch(5)