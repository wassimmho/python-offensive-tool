#!/usr/bin/env python3
"""
Exhaustive brute-force tester (attempts all combinations for given charset and length range).
Safe defaults: single-threaded, rate-limited, CSV logging, checkpoint/resume capability.

WARNING: combinations grow exponentially. Use small charset and short lengths first.
Run only on systems you own or are explicitly authorized to test.
"""

import itertools
import requests
import time
import csv
import sys
import os
from math import prod
from tasks import app, brute_force_chunk
from celery import group
import math

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- Import config ---
try:
    from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHARSET, MIN_LEN, MAX_LEN, USERNAME, TARGET_URL, PASSWORD_FIELD, USERNAME_FIELD, TIMEOUT
    # Try to import additional config variables with fallbacks
    try:
        from config import DELAY_SECONDS, PASSWORD_LIST_CHECKPOINT, CSV_OUT, RESUME_FROM, USE_SELENIUM, USE_HYBRID
    except ImportError:
        DELAY_SECONDS = 0.5
        PASSWORD_LIST_CHECKPOINT = "bf_checkpoint.txt"
        CSV_OUT = "exhaustive_bf_results.csv"
        RESUME_FROM = None
        USE_SELENIUM = False
        USE_HYBRID = False
except ImportError:
    # fallback for direct script usage
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CHARSET = "abcdefghijklmnopqrstuwvxyz0123456789"
    MIN_LEN = 6
    MAX_LEN = 6
    USERNAME = "testuser@gmail.com"
    TARGET_URL = "http://127.0.0.1:5000/signin"
    PASSWORD_FIELD = "password"
    USERNAME_FIELD = "email"  # Fixed: your form uses email
    TIMEOUT = 10
    DELAY_SECONDS = 0.5
    PASSWORD_LIST_CHECKPOINT = "bf_checkpoint.txt"
    CSV_OUT = "exhaustive_bf_results.csv"
    RESUME_FROM = None
    USE_SELENIUM = False
    USE_HYBRID = False

# ----------------- safety helper -----------------
def estimate_total(charset_len, min_l, max_l):
    totals = [(charset_len ** L) for L in range(min_l, max_l + 1)]
    return sum(totals), totals

# ----------------- generator -----------------
def candidate_generator(charset, min_len, max_len, resume_from=None):
    started = resume_from is None
    for L in range(min_len, max_len + 1):
        # itertools.product returns tuples of characters; join to make strings
        for tup in itertools.product(charset, repeat=L):
            pwd = ''.join(tup)
            if not started:
                if pwd == resume_from:
                    started = True
                    yield pwd
                else:
                    continue
            else:
                yield pwd

# ----------------- attempt single password -----------------
def attempt(session, password, use_selenium=False):
    """
    Attempt to login with given password
    use_selenium: If True, uses Selenium for JavaScript-heavy sites
    """
    
    if use_selenium:
        return selenium_attempt(password)
    
    # Original requests-based attempt
    payload = {USERNAME_FIELD: USERNAME, PASSWORD_FIELD: password}
    try:
        resp = session.post(TARGET_URL, data=payload, timeout=TIMEOUT, allow_redirects=False)
    except Exception as e:
        return False, None, f"error:{e}"

    status = resp.status_code
    success = False
    reason = ""

    # 1) JSON check (best)
    try:
        j = resp.json()
        if isinstance(j, dict) and j.get("success") is True:
            return True, status, "json_success"
        reason = j.get("reason") if isinstance(j, dict) else reason
    except Exception:
        pass

    # 2) Redirect check (common)
    if status in (301, 302, 303, 307):
        loc = (resp.headers.get("Location") or "").lower()
        if any(k in loc for k in ("dashboard", "profile", "home", "welcome")):
            return True, status, f"redirect->{loc}"

    # 3) Cookie check — did server set a session cookie?
    if any(k in session.cookies.get_dict() for k in ("session", "sessionid", "flask_session")):
        return True, status, "session_cookie_set"

    # 4) Body content check — change keywords to match your app
    body = resp.text or ""
    body_lower = body.lower()
    if any(term in body_lower for term in ["login successful", "welcome", "dashboard", "success"]):
        return True, status, "body_contains_success"
    
    # 5) Check for error messages (to distinguish between different failure types)
    if any(term in body_lower for term in ["invalid", "wrong password", "incorrect"]):
        reason = "invalid_credentials"

    # otherwise: treat as failure
    return False, status, reason or "no_success_indicators"


def selenium_attempt(password):
    """Attempt login using Selenium with VISIBLE browser window"""
    driver = None
    try:
        # Set up Chrome options - VISIBLE browser
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        
        # REMOVED headless mode - browser will be visible
        # chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")  # Start maximized
        
        # Optional: Disable extensions for cleaner testing
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        print(f"🔍 Launching Chrome browser for password: {password}")
        
        # FIX: Use 'options' parameter (newer Selenium versions)
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"🌐 Navigating to: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Debug: Print page title and URL
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Find input fields - try multiple selectors
        print("🔎 Looking for form fields...")
        selectors_to_try = [
            (By.NAME, "email"),
            (By.NAME, "username"), 
            (By.ID, "email"),
            (By.ID, "username"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.XPATH, "//input[@placeholder='Email']"),
            (By.XPATH, "//input[@placeholder='Username']")
        ]
        
        username_field = None
        password_field = None
        
        for by, value in selectors_to_try:
            try:
                if not username_field:
                    username_field = driver.find_element(by, value)
                    print(f"✅ Found username field with: {by}='{value}'")
            except Exception as e:
                continue
                
        # Find password field
        password_selectors = [
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.ID, "password"),
            (By.XPATH, "//input[@placeholder='Password']")
        ]
        
        for by, value in password_selectors:
            try:
                if not password_field:
                    password_field = driver.find_element(by, value)
                    print(f"✅ Found password field with: {by}='{value}'")
                    break
            except Exception as e:
                continue
        
        if not username_field:
            print("❌ Could not find username field!")
            # Take screenshot for debugging
            driver.save_screenshot("debug_no_username_field.png")
            driver.quit()
            return False, None, "selenium_username_field_not_found"
            
        if not password_field:
            print("❌ Could not find password field!")
            # Take screenshot for debugging
            driver.save_screenshot("debug_no_password_field.png")
            driver.quit()
            return False, None, "selenium_password_field_not_found"
        
        # Clear and fill form with visible typing
        print(f"⌨️  Typing username: {USERNAME}")
        username_field.clear()
        username_field.send_keys(USERNAME)
        time.sleep(0.5)  # Slightly longer delay to see typing
        
        print(f"⌨️  Typing password: {password}")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.5)  # Slightly longer delay to see typing
        
        # Submit form (try multiple methods)
        print("🚀 Submitting form...")
        submitted = False
        
        try:
            # Method 1: Press Enter in password field
            print("   Trying Enter key...")
            password_field.send_keys(Keys.ENTER)
            submitted = True
            print("   ✅ Submitted with Enter key")
        except Exception as e:
            print(f"   ❌ Enter key failed: {e}")
        
        if not submitted:
            try:
                # Method 2: Find and click submit button
                print("   Looking for submit button...")
                submit_buttons = [
                    (By.CSS_SELECTOR, "button[type='submit']"),
                    (By.CSS_SELECTOR, "input[type='submit']"),
                    (By.CSS_SELECTOR, "button"),
                    (By.ID, "submit"),
                    (By.CLASS_NAME, "btn-primary"),
                    (By.CLASS_NAME, "btn"),
                    (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                    (By.XPATH, "//button[contains(text(), 'Login')]"),
                    (By.XPATH, "//input[@type='submit']")
                ]
                
                for by, value in submit_buttons:
                    try:
                        submit_btn = driver.find_element(by, value)
                        print(f"   ✅ Found submit button with: {by}='{value}'")
                        submit_btn.click()
                        submitted = True
                        print(f"   ✅ Clicked submit button")
                        break
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"   ❌ Submit button click failed: {e}")
        
        # Wait for response
        print("⏳ Waiting for response...")
        time.sleep(3)
        
        # Debug: Print new page info
        print(f"📄 New page title: {driver.title}")
        print(f"🔗 New URL: {driver.current_url}")
        
        # Check for success indicators
        success_indicators = []
        
        # 1) URL changed (redirect happened)
        current_url = driver.current_url.lower()
        original_url = TARGET_URL.lower()
        if current_url != original_url:
            success_indicators.append(f"redirected_to_{current_url}")
            print(f"🔄 Redirect detected: {current_url}")
        
        # 2) Check for success elements in page
        page_source = driver.page_source.lower()
        success_keywords = ["welcome", "dashboard", "profile", "success", "logout", "signed in", "logged in"]
        for keyword in success_keywords:
            if keyword in page_source:
                success_indicators.append(f"page_contains_{keyword}")
                print(f"✅ Success keyword found: {keyword}")
        
        # 3) Check for session cookies
        cookies = driver.get_cookies()
        session_cookies = [cookie for cookie in cookies if 'session' in cookie['name'].lower()]
        if session_cookies:
            success_indicators.append("session_cookie_set")
            print(f"🍪 Session cookie found: {[c['name'] for c in session_cookies]}")
        
        # 4) Check page title for success indicators
        page_title = driver.title.lower()
        if any(term in page_title for term in ["dashboard", "welcome", "profile", "home"]):
            success_indicators.append("successful_page_title")
            print(f"📝 Success page title: {driver.title}")
        
        # 5) Check for error messages
        error_indicators = ["invalid", "wrong", "incorrect", "error", "failed"]
        has_errors = any(error in page_source for error in error_indicators)
        if has_errors:
            print("❌ Error message detected on page")
        
        success = len(success_indicators) > 0
        reason = "selenium_success" if success else "selenium_failed"
        if success_indicators:
            reason += ":" + ",".join(success_indicators)
        elif has_errors:
            reason = "invalid_credentials"
        
        # Take final screenshot for debugging
        if success:
            driver.save_screenshot(f"success_{password}.png")
            print(f"📸 Success screenshot saved: success_{password}.png")
        else:
            driver.save_screenshot(f"failed_{password}.png")
            print(f"📸 Failure screenshot saved: failed_{password}.png")
        
        print(f"🎯 Result for '{password}': success={success}, reason={reason}")
        driver.quit()
        return success, 200 if success else 401, reason
        
    except Exception as e:
        print(f"💥 Selenium error for '{password}': {str(e)}")
        if driver:
            try:
                # Take error screenshot
                driver.save_screenshot(f"error_{password}.png")
                print(f"📸 Error screenshot saved: error_{password}.png")
                driver.quit()
            except:
                pass
        return False, None, f"selenium_error:{str(e)}"
    
def hybrid_attempt(session, password):
    """
    Try requests first, fall back to Selenium if requests fail 
    or if we detect JavaScript requirements
    """
    # First try with requests (faster)
    success, status, reason = attempt(session, password, use_selenium=False)
    
    # If requests fail with certain errors, try Selenium
    if not success and any(x in reason for x in ["javascript", "timeout", "connection"]):
        print(f"  Requests failed with '{reason}', trying Selenium for {password}...")
        return selenium_attempt(password)
    
    return success, status, reason

# --- Helper: split prefixes for chunking ---
def get_prefixes(length, num_workers):
    charset_size = len(CHARSET)
    if length <= 2 or charset_size ** length <= num_workers:
        return [""]
    prefix_len = min(length, math.ceil(math.log(num_workers) / math.log(charset_size)))
    return ["".join(p) for p in itertools.product(CHARSET, repeat=prefix_len)]

# --- Celery Task: chunked brute-force ---

# --- Distributed main ---
def distributed_bruteforce(num_workers):
    print(f"Distributed brute-force: charset={CHARSET}, min_len={MIN_LEN}, max_len={MAX_LEN}, workers={num_workers}")
    for length in range(MIN_LEN, MAX_LEN + 1):
        prefixes = get_prefixes(length, num_workers)
        print(f"Length {length}: {len(prefixes)} chunks")
        tasks = [
            brute_force_chunk.s(
                USERNAME, TARGET_URL, PASSWORD_FIELD, USERNAME_FIELD,
                CHARSET, length, prefix, TIMEOUT
            )
            for prefix in prefixes
        ]
        job = group(tasks)
        result = job.apply_async()
        print(f"Submitted {len(prefixes)} tasks for length {length}. Waiting for results...")
        found = None
        for res in result.get():
            if res:
                found = res
                break
        if found:
                try:
                    requests.post(TARGET_URL, json={"username": USERNAME, "password": found})
                except Exception as e:
                    print(f"Failed to notify success endpoint: {e}")
                return found
    print("Password not found in distributed search.")
    return None

# ----------------- main runner -----------------
def main():
    charset_len = len(CHARSET)
    total, breakdown = estimate_total(charset_len, MIN_LEN, MAX_LEN)

    # Print configuration for debugging
    print(f"Configuration:")
    print(f"  PASSWORD_LIST_CHECKPOINT: {PASSWORD_LIST_CHECKPOINT}")
    print(f"  CSV_OUT: {CSV_OUT}")
    print(f"  USERNAME_FIELD: {USERNAME_FIELD}")
    print(f"  TARGET_URL: {TARGET_URL}")
    print(f"  Using Selenium: {USE_SELENIUM}")
    print(f"  Using Hybrid: {USE_HYBRID}")

    if not os.path.exists(PASSWORD_LIST_CHECKPOINT):
        open(PASSWORD_LIST_CHECKPOINT, "a", encoding="utf-8").close()

    if not os.path.exists(CSV_OUT):
        with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp","username","password","status","success","reason", "method"])
            writer.writeheader()

    print(f"Charset length: {charset_len}. Trying lengths {MIN_LEN}..{MAX_LEN}.")
    print(f"Total combinations: {total}")
    for L, cnt in enumerate(breakdown, start=MIN_LEN):
        print(f" length {L}: {cnt} combos")
    if total > 100_000_000:
        print("WARNING: total combos > 100 million. This may take a very long time.")
        print("Please reduce charset/length or use targeted wordlists. Abort now with Ctrl+C if unintended.")
        time.sleep(2)

    # handle resume
    resume = RESUME_FROM
    if os.path.exists(PASSWORD_LIST_CHECKPOINT):
        try:
            with open(PASSWORD_LIST_CHECKPOINT, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved:
                    resume = saved
                    print(f"Resuming from checkpoint password: {resume}")
        except Exception:
            pass
    if resume:
        print(f"Resuming from: {resume}")

    session = requests.Session()
    with open(CSV_OUT, "a", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=["timestamp","username","password","status","success","reason", "method"])
        if csvf.tell() == 0:  # File is empty
            writer.writeheader()

        gen = candidate_generator(CHARSET, MIN_LEN, MAX_LEN, resume_from=resume)
        count = 0
        start_time = time.time()
        for pwd in gen:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Choose attempt method based on configuration
            if USE_SELENIUM:
                success, status, reason = selenium_attempt(pwd)
                method = "selenium"
            elif USE_HYBRID:
                success, status, reason = hybrid_attempt(session, pwd)
                method = "hybrid"
            else:
                success, status, reason = attempt(session, pwd, use_selenium=False)
                method = "requests"

            # write attempt
            writer.writerow({
                "timestamp": ts,
                "username": USERNAME,
                "password": pwd,
                "status": status,
                "success": success,
                "reason": reason,
                "method": method
            })
            csvf.flush()
            count += 1

            # update checkpoint
            try:
                with open(PASSWORD_LIST_CHECKPOINT, "w", encoding="utf-8") as ck:
                    ck.write(pwd)
            except Exception:
                pass

            # console output
            elapsed = time.time() - start_time
            tries_per_sec = count / elapsed if elapsed > 0 else 0
            print(f"[{ts}] [{method}] tried: {pwd} -> success={success} status={status} reason={reason}  total_tried={count} rate={tries_per_sec:.2f}/s")

            if success:
                print("+++ FOUND password:", pwd)
                try:
                    requests.post("http://127.0.0.1:5000/signin", json={"username": USERNAME, "password": pwd})
                except Exception as e:
                    print(f"Failed to notify success endpoint: {e}")
                try:
                    os.remove(PASSWORD_LIST_CHECKPOINT)
                except Exception:
                    pass
                break

            time.sleep(DELAY_SECONDS)

    print("Finished. Attempts:", count)

# --- CLI Entrypoint ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--distributed", action="store_true", help="Use distributed Celery brute-force")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers/chunks")
    parser.add_argument("--selenium", action="store_true", help="Use Selenium instead of requests")
    parser.add_argument("--hybrid", action="store_true", help="Use hybrid approach (requests first, Selenium fallback)")
    args = parser.parse_args()
    
    if args.selenium:
        USE_SELENIUM = True
        USE_HYBRID = False
    elif args.hybrid:
        USE_SELENIUM = False
        USE_HYBRID = True
    
    if args.distributed:
        distributed_bruteforce(args.workers)
    else:
        main()