# tests/test_courses_e2e.py
import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
class TestCoursesE2E:
    def test_courses_display(self, page: Page, live_server, courses):
        # Use the courses fixture - it gives you 5 pre-created courses
        page.goto(f"{live_server.url}/")
        
        # Verify all courses from the fixture are visible
        for course in courses:
            expect(page.locator(f"text={course.name}")).to_be_visible()
            expect(page.locator(f"text={course.code}")).to_be_visible()

    
    def test_course_detail_display_with_navigation(self, page: Page, live_server, course):
        # Use the course fixture - it gives you a pre-created course
        page.goto(f"{live_server.url}/")
        
        # Click on the course created by the fixture
        page.click(f"text={course.name}")
        
        # Verify we're on detail page
        expect(page).to_have_url(f"{live_server.url}/reviews/courses/{course.code}/")
        expect(page.locator("h1")).to_contain_text(course.name)
        expect(page.locator("text=" + course.description)).to_be_visible()



