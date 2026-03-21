from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def fetch_rendered_html(url: str, table_selector: str) -> str:
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(url)
        # optional cookies click
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept All Cookies')]"))
            ).click()
        except Exception:
            pass
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
        )
        return driver.page_source
    finally:
        driver.quit()
    

def fetch_rendered_html_debug(url, table_selector):
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 45)

        # Confirm page shell loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Optional: attempt cookie-banner dismissal
        cookie_candidates = [
            "button#onetrust-accept-btn-handler",
            "button[aria-label*='Accept']",
            "button[title*='Accept']",
            "button[data-testid*='accept']",
        ]

        for selector in cookie_candidates:
            try:
                btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                btn.click()
                print(f"Clicked cookie button: {selector}")
                break
            except Exception:
                pass

        # Wait for target
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector)))

        return driver.page_source

    except TimeoutException:
        print("=== TIMEOUT DEBUG ===")
        print("URL:", driver.current_url)
        print("TITLE:", driver.title)
        print("SELECTOR:", table_selector)

        # See if any tables exist at all
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            print("Number of <table> elements found:", len(tables))
        except Exception as e:
            print("Error counting tables:", e)

        # Dump some page source
        src = driver.page_source
        print("Page source first 8000 chars:")
        print(src[:8000])

        driver.save_screenshot("timeout_debug.png")
        raise
    finally:
        driver.quit()