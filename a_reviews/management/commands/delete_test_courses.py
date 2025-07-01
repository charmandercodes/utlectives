from django.core.management.base import BaseCommand
from django.db import transaction
from a_reviews.models import Course  # Adjust import path to your app


class Command(BaseCommand):
    help = 'Delete test courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete ALL courses (use with caution!)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Delete courses with codes matching this pattern (e.g., "CS*" for all CS courses)'
        )
        parser.add_argument(
            '--faculty',
            type=str,
            choices=['Analytics', 'Business', 'Engineering', 'Law', 'Health', 'Science', 'IT'],
            help='Delete courses from a specific faculty'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        # Build query based on options
        queryset = Course.objects.all()
        
        if options['pattern']:
            pattern = options['pattern'].replace('*', '')
            queryset = queryset.filter(code__startswith=pattern)
            filter_desc = f"courses with code starting with '{pattern}'"
        elif options['faculty']:
            queryset = queryset.filter(faculty=options['faculty'])
            filter_desc = f"courses from {options['faculty']} faculty"
        elif options['all']:
            filter_desc = "ALL courses"
        else:
            # Default: delete test courses (courses with randomly generated codes)
            test_prefixes = ['CS', 'IT', 'BUS', 'LAW', 'SCI', 'ENG', 'HLT']
            # Filter for courses that look like test data (5-digit numbers after prefix)
            import re
            test_courses = []
            for course in Course.objects.all():
                for prefix in test_prefixes:
                    if re.match(f'^{prefix}\\d{{5}}$', course.code):
                        test_courses.append(course.id)
                        break
            
            queryset = Course.objects.filter(id__in=test_courses)
            filter_desc = "test courses (with auto-generated codes)"

        course_count = queryset.count()
        
        if course_count == 0:
            self.stdout.write(
                self.style.WARNING("No courses found matching the criteria.")
            )
            return

        # Show what will be deleted
        self.stdout.write(f"\nFound {course_count} {filter_desc}:")
        
        # Display sample courses that will be deleted
        sample_courses = list(queryset[:10])
        for course in sample_courses:
            self.stdout.write(f"  - {course.code}: {course.name}")
        
        if course_count > 10:
            self.stdout.write(f"  ... and {course_count - 10} more")

        # Confirmation
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f"\nThis will permanently delete {course_count} courses!"
                )
            )
            confirm = input("Are you sure you want to continue? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write("Operation cancelled.")
                return

        # Delete courses
        with transaction.atomic():
            deleted_count, deleted_details = queryset.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted_count} courses!"
            )
        )
        
        # Show breakdown of what was deleted
        if deleted_details:
            self.stdout.write("\nDeleted:")
            for model, count in deleted_details.items():
                if count > 0:
                    self.stdout.write(f"  - {model}: {count}")


# Additional utility command for more targeted deletion
class Command(BaseCommand):
    help = 'Delete test courses with various filtering options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete ALL courses (use with extreme caution!)'
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Delete only test courses (auto-generated codes)'
        )
        parser.add_argument(
            '--code-pattern',
            type=str,
            help='Delete courses with codes matching pattern (e.g., "CS1" for CS1****)'
        )
        parser.add_argument(
            '--faculty',
            type=str,
            choices=['Analytics', 'Business', 'Engineering', 'Law', 'Health', 'Science', 'IT'],
            help='Delete courses from specific faculty'
        )
        parser.add_argument(
            '--rating-below',
            type=float,
            help='Delete courses with overall rating below this value'
        )
        parser.add_argument(
            '--no-reviews',
            action='store_true',
            help='Delete courses that have no reviews'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        # Build query
        queryset = Course.objects.all()
        filters_applied = []

        if options['test_only']:
            # Match auto-generated course codes
            import re
            test_prefixes = ['CS', 'IT', 'BUS', 'LAW', 'SCI', 'ENG', 'HLT']
            test_course_ids = []
            
            for course in Course.objects.all():
                for prefix in test_prefixes:
                    if re.match(f'^{prefix}\\d{{5}}$', course.code):
                        test_course_ids.append(course.id)
                        break
            
            queryset = queryset.filter(id__in=test_course_ids)
            filters_applied.append("test courses only")
            
        if options['code_pattern']:
            pattern = options['code_pattern']
            queryset = queryset.filter(code__startswith=pattern)
            filters_applied.append(f"code starts with '{pattern}'")
            
        if options['faculty']:
            queryset = queryset.filter(faculty=options['faculty'])
            filters_applied.append(f"faculty = {options['faculty']}")
            
        if options['rating_below']:
            queryset = queryset.filter(overall_rating__lt=options['rating_below'])
            filters_applied.append(f"rating < {options['rating_below']}")
            
        if options['no_reviews']:
            queryset = queryset.filter(review__isnull=True)
            filters_applied.append("no reviews")

        if not filters_applied and not options['all']:
            self.stdout.write(
                self.style.ERROR(
                    "No filters specified. Use --test-only, --all, or other filters."
                )
            )
            return

        course_count = queryset.count()
        
        if course_count == 0:
            self.stdout.write(
                self.style.WARNING("No courses found matching the criteria.")
            )
            return

        # Display results
        filter_description = " AND ".join(filters_applied) if filters_applied else "ALL courses"
        self.stdout.write(f"\nFilters: {filter_description}")
        self.stdout.write(f"Found {course_count} courses to delete:")
        
        # Show sample
        for course in queryset[:5]:
            self.stdout.write(
                f"  - {course.code}: {course.name} ({course.faculty}) "
                f"Rating: {course.overall_rating}"
            )
        
        if course_count > 5:
            self.stdout.write(f"  ... and {course_count - 5} more")

        # Dry run check
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS("DRY RUN - No courses were actually deleted.")
            )
            return

        # Confirmation
        if not options['force']:
            if options['all']:
                self.stdout.write(
                    self.style.ERROR(
                        f"\n⚠️  WARNING: This will delete ALL {course_count} courses! ⚠️"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"\nThis will permanently delete {course_count} courses."
                    )
                )
            
            confirm = input("Type 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                self.stdout.write("Operation cancelled.")
                return

        # Perform deletion
        with transaction.atomic():
            deleted_count, _ = queryset.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted_count} courses!"
            )
        )