from django.core.management.base import BaseCommand
from django.db import transaction
from a_reviews.models import Course, Review  # adjust import path

class Command(BaseCommand):
    help = 'Delete all courses except those with reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        # Find courses that have reviews (using the reverse foreign key)
        courses_with_reviews = Course.objects.filter(
            review__isnull=False
        ).distinct()
        
        # Find courses without reviews
        courses_to_delete = Course.objects.filter(
            review__isnull=True
        )
        
        self.stdout.write(f"Courses with reviews (keeping): {courses_with_reviews.count()}")
        self.stdout.write(f"Courses to delete: {courses_to_delete.count()}")
        
        if courses_with_reviews.exists():
            self.stdout.write("Keeping courses:")
            for course in courses_with_reviews:
                review_count = course.review_set.count()
                self.stdout.write(f"  - {course.code}: {course.name} ({review_count} reviews)")
        
        if options['dry_run']:
            self.stdout.write("DRY RUN - would delete:")
            for course in courses_to_delete[:10]:  # show first 10
                self.stdout.write(f"  - {course.code}: {course.name}")
            if courses_to_delete.count() > 10:
                self.stdout.write(f"  ... and {courses_to_delete.count() - 10} more")
            return
        
        # Actually delete
        with transaction.atomic():
            deleted_count, _ = courses_to_delete.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} courses')
            )