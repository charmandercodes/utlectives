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
            self.click_subject_links(driver)
            
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
    
    def get_subject_details(self, driver):
        """Extract and print subject details from the current page"""
        try:
            # Wait a bit for page to fully load
            time.sleep(1)
            
            # Get title
            try:
                title_element = driver.find_element(By.CSS_SELECTOR, "h2[data-testid='ai-header']")
                title = title_element.text
                self.stdout.write(f"  Title: {title}")
            except Exception as e:
                self.stdout.write(f"  Could not find title: {e}")
            
            # Get faculty

            try:
                faculty_element = driver.find_element(By.XPATH, "//*[@id='flex-around-rhs']/aside/div/div/div[1]/div")
                faculty = faculty_element.text
                self.stdout.write(f"  Faculty: {faculty}")
            except Exception as e:
                self.stdout.write(f"  Could not find faculty: {e}")
            
            
            # # Get description
            # try:
            #     description_element = driver.find_element(By.CSS_SELECTOR, "#Subjectdescription > div.css-1wk50yi-Box--Box-Box-Card--CardBody.e12hqxty1 > div.unset.css-pklc5t-ReadMore--Body.e1ydu1r41 > div")
            #     description = description_element.text
            #     self.stdout.write(f"  Description: {description}")
            # except Exception as e:
            #     self.stdout.write(f"  Could not find description: {e}")
                
        except Exception as e:
            self.stdout.write(f"  Error extracting subject details: {e}")
        
        self.stdout.write("  ---")  # Separator between subjects
    

    def click_subject_links(self, driver):
        """Find and click on subject links after they load"""
        self.stdout.write("Waiting for subject results to load...")
        wait = WebDriverWait(driver, 15)
        
        # Wait for search results to appear
        time.sleep(3)
        
        try:
            # Find all subject containers using the search-results pattern
            subject_containers = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search-results > div"))
            )
            
            self.stdout.write(f"Found {len(subject_containers)} subject containers")
            
            # Click on first 3 subjects for testing
            for i, container in enumerate(subject_containers[:3]):
                try:
                    # Find the link within this container using a more specific selector
                    subject_link = container.find_element(By.CSS_SELECTOR, "a[role='navigation']")
                    subject_title = container.find_element(By.CSS_SELECTOR, ".result-item-title").text
                    
                    self.stdout.write(f"Clicking on subject {i+1}: {subject_title}")
                    
                    # Click the subject link
                    subject_link.click()
                    
                    # Wait for page to load
                    time.sleep(2)
                    self.get_subject_details(driver)
                    
                    # Go back to results page
                    driver.back()
                    
                    # Wait for results to reload
                    time.sleep(2)
                    
                    # Re-find containers since we navigated back
                    subject_containers = driver.find_elements(By.CSS_SELECTOR, "#search-results > div")
                    
                except Exception as e:
                    self.stdout.write(f"Error clicking subject {i+1}: {e}")
                    continue
                    
        except Exception as e:
            self.stdout.write(f"Error finding subject containers: {e}")
    


    
        
