import json
from django.core.management.base import BaseCommand
from a_reviews.models import Course

class Command(BaseCommand):
    help = "Import courses from a JSON file or delete all courses"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the JSON file containing courses'
        )
        parser.add_argument(
            '--delete-all',
            action='store_true',
            help='Delete all courses from the database'
        )

    def handle(self, *args, **options):
        # Handle deletion first
        if options['delete_all']:
            count, _ = Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} courses from the database."))
            # Exit if only deleting
            if not options['file']:
                return

        file_path = options['file']
        if not file_path:
            self.stderr.write("Please provide the path to the JSON file using --file")
            return

        # Load JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)

        for course_item in courses_data:
            code = course_item.get("code")
            title = course_item.get("title")
            description = course_item.get("description", "")
            teaching_period = course_item.get("teachingPeriod", "")
            base_url = "https://coursehandbook.uts.edu.au"
            url_path = course_item.get("URL_MAP_FOR_CONTENT", "")
            full_url = base_url + url_path
            faculty = course_item.get("educationalAreaDisplay", "")

            # Create or update the Course
            course, created = Course.objects.update_or_create(
                code=code,
                defaults={
                    'name': title,
                    'description': description,
                    'page_reference': full_url,
                    'faculty': faculty,
                    'sessions': teaching_period if teaching_period else [],

                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created course {code} - {title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated course {code} - {title}"))

        self.stdout.write(self.style.SUCCESS("Import complete."))
