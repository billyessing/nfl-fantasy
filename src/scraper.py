import time
import logging
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

class NFLFantasyScraper:
    """Web scraper for NFL.com fantasy league data"""
    
    def __init__(self, league_id: str, session_cookies: Dict[str, str] = None, username: str = None, password: str = None):
        self.league_id = league_id
        self.session_cookies = session_cookies or {}
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.rate_limit = float(os.getenv('RATE_LIMIT', '2.0'))
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def init_driver(self, headless: bool = True):
        """Initialize Chrome WebDriver"""
        try:
            options = Options()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            
            # Add session cookies if provided
            if self.session_cookies:
                self.driver.get('https://fantasy.nfl.com')
                for name, value in self.session_cookies.items():
                    self.driver.add_cookie({'name': name, 'value': value})
                    
            self.logger.info("WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def close_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def authenticate_with_cookies(self, cookies: Dict[str, str]):
        """Set session cookies for authentication"""
        self.session_cookies = cookies
        if self.driver:
            self.driver.get('https://fantasy.nfl.com')
            for name, value in cookies.items():
                self.driver.add_cookie({'name': name, 'value': value})
    
    def login_with_credentials(self):
        """Login to NFL.com using username and password"""
        if not self.username or not self.password:
            self.logger.error("Username and password required for credential login")
            return False
            
        try:
            self.logger.info("Attempting to login with credentials")
            self.driver.get('https://www.nfl.com/account/sign-in')
            
            # Wait for page to load
            time.sleep(5)
            
            # Try different selectors for email field
            username_field = None
            email_selectors = [
                "input[type='email']",
                "input[name='email']", 
                "input[id='email']",
                "input[placeholder*='email' i]",
                "input[placeholder*='Email' i]"
            ]
            
            for selector in email_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found email field with selector: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                self.logger.error("Could not find email field")
                return False
            
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Try different selectors for password field  
            password_field = None
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[id='password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found password field with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                self.logger.error("Could not find password field")
                return False
                
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Try different selectors for submit button
            login_button = None
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']", 
                "button:contains('Sign In')",
                "button:contains('Login')",
                "button:contains('Log In')"
            ]
            
            for selector in button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found login button with selector: {selector}")
                    break
                except:
                    continue
            
            if not login_button:
                self.logger.error("Could not find login button")
                return False
                
            login_button.click()
            
            # Wait for login to complete
            time.sleep(10)
            
            # Check if we're logged in by looking for common post-login elements
            login_success_indicators = [
                "//a[contains(@href, 'account')]",
                "//a[contains(@href, 'profile')]", 
                "//button[contains(text(), 'Sign Out')]",
                "//a[contains(text(), 'Sign Out')]"
            ]
            
            for indicator in login_success_indicators:
                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, indicator)))
                    self.logger.info("Successfully logged in")
                    return True
                except:
                    continue
                    
            self.logger.error("Login may have failed - no success indicators found")
            return False
                
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False
    
    def get_league_url(self, year: Optional[int] = None, page: str = '') -> str:
        """Generate NFL.com fantasy league URLs"""
        base_url = f"https://fantasy.nfl.com/league/{self.league_id}"
        
        if year:
            if page == 'standings':
                return f"{base_url}?season={year}&view=standings"
            elif page == 'schedule':
                return f"{base_url}?season={year}&view=schedule"
            elif page:
                return f"{base_url}/history/{year}/{page}"
            else:
                return f"{base_url}?season={year}"
        else:
            if page:
                return f"{base_url}/{page}"
            else:
                return base_url
    
    def load_page(self, url: str, wait_for_element: str = None) -> Optional[BeautifulSoup]:
        """Load a page and return BeautifulSoup object"""
        try:
            self.logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for JavaScript to load
            time.sleep(2)
            
            # Wait for specific element if provided
            if wait_for_element:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
            return soup
            
        except TimeoutException:
            self.logger.error(f"Timeout loading page: {url}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading page {url}: {e}")
            return None
    
    def extract_league_info(self) -> Optional[Dict]:
        """Extract basic league information"""
        url = self.get_league_url()
        soup = self.load_page(url)
        
        if not soup:
            return None
            
        league_info = {
            'league_id': self.league_id,
            'name': None,
            'owners': [],
            'seasons': []
        }
        
        try:
            # Extract league name
            league_name_elem = soup.find('h1', class_='leagueName') or soup.find('title')
            if league_name_elem:
                league_info['name'] = league_name_elem.get_text().strip()
            
            # Extract team owners from standings or roster pages
            # This will need to be customized based on actual HTML structure
            owner_elements = soup.find_all('a', href=lambda x: x and '/team/' in x)
            for elem in owner_elements:
                owner_info = {
                    'name': elem.get_text().strip(),
                    'team_id': self._extract_team_id_from_url(elem.get('href', ''))
                }
                if owner_info['name'] and owner_info not in league_info['owners']:
                    league_info['owners'].append(owner_info)
            
            return league_info
            
        except Exception as e:
            self.logger.error(f"Error extracting league info: {e}")
            return league_info
    
    def extract_season_standings(self, year: int) -> List[Dict]:
        """Extract season standings for a specific year"""
        url = self.get_league_url(year, 'standings')
        soup = self.load_page(url, '.tableWrap')
        
        if not soup:
            return []
        
        standings = []
        
        try:
            # Look for standings table
            table = soup.find('table') or soup.find('div', class_='tableWrap')
            if not table:
                self.logger.warning(f"No standings table found for {year}")
                return []
            
            # Extract team standings data
            rows = table.find_all('tr')[1:]  # Skip header row
            for i, row in enumerate(rows, 1):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    standing = {
                        'rank': i,
                        'team_name': cells[0].get_text().strip(),
                        'record': cells[1].get_text().strip() if len(cells) > 1 else '',
                        'points_for': self._extract_points(cells[2].get_text()) if len(cells) > 2 else 0,
                        'season': year
                    }
                    standings.append(standing)
            
            return standings
            
        except Exception as e:
            self.logger.error(f"Error extracting standings for {year}: {e}")
            return []
    
    def extract_matchup_data(self, year: int, week: int) -> List[Dict]:
        """Extract matchup data for a specific week"""
        # This would need to be implemented based on actual NFL.com structure
        # For now, return empty list as placeholder
        self.logger.info(f"Extracting matchups for {year} week {week}")
        return []
    
    def _extract_team_id_from_url(self, url: str) -> str:
        """Extract team ID from NFL.com URL"""
        if '/team/' in url:
            parts = url.split('/team/')
            if len(parts) > 1:
                return parts[1].split('/')[0]
        return ''
    
    def _extract_points(self, text: str) -> float:
        """Extract point values from text"""
        try:
            # Remove non-numeric characters except decimal point
            cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def get_available_seasons(self) -> List[int]:
        """Get list of available seasons for the league"""
        # This would need to inspect league history pages
        # For now return placeholder
        current_year = 2024
        return list(range(2015, current_year + 1))  # Placeholder range