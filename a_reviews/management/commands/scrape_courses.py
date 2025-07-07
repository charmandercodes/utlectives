from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = 'Simple scraper that opens a URL with Selenium'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            required=True,
            help='URL to scrape'
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode (no GUI)'
        )

    def handle(self, *args, **options):
        url = options['url']
        headless = options['headless']
        
        self.stdout.write(f"Opening URL with Selenium: {url}")
        
        # Set up Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        driver = None
        try:
            # Create webdriver instance
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to the URL
            driver.get(url)
            
            self.stdout.write(f"Page title: {driver.title}")
            self.stdout.write(f"Current URL: {driver.current_url}")
            
            # Wait a bit to see the page (if not headless)
            if not headless:
                self.stdout.write("Browser window opened. Waiting 10 seconds...")
                time.sleep(10)
            
            # Get page source length
            page_source = driver.page_source
            self.stdout.write(f"Page source length: {len(page_source)} characters")
            
        except Exception as e:
            self.stdout.write(f"Error: {e}")
        finally:
            if driver:
                driver.quit()
                self.stdout.write("Browser closed.")