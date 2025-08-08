import pytest
from django.urls import reverse
from a_reviews.models import Course


###################### Read tests


# Read courses Test
@pytest.mark.django_db
def test_courses_displayed_on_page(client, courses):
    
    response = client.get(reverse('course-list'))


    assert response.status_code == 200

    content = response.content.decode()

    for course in courses:
        assert course.name in content



# Read course detail test

# read reviews test

###################### Create review tests

###################### Update review tests


###################### Delete review tests



