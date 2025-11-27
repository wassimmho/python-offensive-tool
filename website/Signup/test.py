from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

def selenium_attempt(password):
    """Attempt login using Selenium (useful for JavaScript-heavy sites)"""
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(TARGET_URL)
        
        # Find input fields - adjust selectors as needed
        username_field = driver.find_element(By.NAME, "email")  # Your form uses "email"
        password_field = driver.find_element(By.NAME, "password")
        
        # Fill form
        username_field.clear()
        username_field.send_keys(USERNAME)
        time.sleep(0.2)
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.2)
        
        # Submit form
        password_field.send_keys(Keys.ENTER)
        time.sleep(3)  # Wait for page load
        
        # Check for success
        success_indicators = [
            driver.current_url != TARGET_URL,  # Redirect happened
            "dashboard" in driver.current_url.lower(),
            "welcome" in driver.page_source.lower(),
            "logout" in driver.page_source.lower(),
            any(cookie['name'].lower() == 'session' for cookie in driver.get_cookies())
        ]
        
        success = any(success_indicators)
        driver.quit()
        return success, 200 if success else 401, "selenium_check"
        
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        return False, None, f"selenium_error:{str(e)}"