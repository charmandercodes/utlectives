from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        
        driver = None
        try:
            driver = self.setup_driver(headless)
            self.navigate_to_page(driver, url)
            self.click_subjects_tab(driver)
            self.display_page_info(driver, headless)
            
        except Exception as e:
            self.stdout.write(f"Error: {e}")
        finally:
            if driver:
                driver.quit()
                self.stdout.write("Browser closed.")

    def setup_driver(self, headless):
        """Set up and return Chrome webdriver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def navigate_to_page(self, driver, url):
        """Navigate to the specified URL and display basic page info"""
        driver.get(url)
        self.stdout.write(f"Page title: {driver.title}")
        self.stdout.write(f"Current URL: {driver.current_url}")

    def click_subjects_tab(self, driver):
        """Find and click the Subjects tab"""
        self.stdout.write("Waiting for 'Subjects' tab to load...")
        wait = WebDriverWait(driver, 10)
        
        subjects_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Subjects')]"))
        )
        subjects_tab.click()
        self.stdout.write("Clicked on 'Subjects' tab")

    def display_page_info(self, driver, headless):
        """Display page information and wait if not headless"""
        if not headless:
            self.stdout.write("Browser window opened. Waiting 10 seconds...")
            time.sleep(10)
        
        page_source = driver.page_source
        self.stdout.write(f"Page source length: {len(page_source)} characters")