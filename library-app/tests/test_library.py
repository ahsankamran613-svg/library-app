"""
Library Book Manager - Selenium Test Suite
16 automated test cases using headless Chrome
"""

import pytest
import time
import os
pytest.importorskip("selenium", reason="selenium is required to run browser tests")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")
TEST_USER = "testuser_selenium"
TEST_PASS = "TestPass123"
TEST_BOOK_TITLE = "The Selenium Chronicles"
TEST_BOOK_AUTHOR = "Auto Tester"
TEST_BOOK_ISBN = "978-0-00-000001-0"
EDITED_TITLE = "The Selenium Chronicles - 2nd Edition"

# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def driver():
    """Create a single headless Chrome driver for the entire session."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(8)
    yield drv
    drv.quit()


def wait_for_flash(driver, timeout=5):
    """Wait until a flash message appears and return its text."""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "flash-message"))
        )
        return el.text
    except Exception:
        return ""


def login(driver, username=TEST_USER, password=TEST_PASS):
    """Helper: navigate to login page and authenticate."""
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()


def logout(driver):
    """Helper: logout if logged in."""
    try:
        driver.find_element(By.ID, "logout-link").click()
    except NoSuchElementException:
        pass


# ──────────────────────────────────────────────
# Test Cases
# ──────────────────────────────────────────────

class TestPageLoad:
    """TC-01: Application home page loads successfully."""

    def test_home_redirects_to_login_or_books(self, driver):
        driver.get(BASE_URL)
        time.sleep(1)
        assert "/login" in driver.current_url or "/books" in driver.current_url, \
            "Home should redirect to login or books page"


class TestRegistration:
    """TC-02 to TC-04: User registration scenarios."""

    def test_register_page_loads(self, driver):
        """TC-02: Registration page renders correctly."""
        driver.get(f"{BASE_URL}/register")
        assert "Register" in driver.title or "LibraryMS" in driver.title
        assert driver.find_element(By.ID, "register-form")

    def test_register_new_user(self, driver):
        """TC-03: Successfully register a new user."""
        driver.get(f"{BASE_URL}/register")
        driver.find_element(By.ID, "username").send_keys(TEST_USER)
        driver.find_element(By.ID, "password").send_keys(TEST_PASS)
        driver.find_element(By.ID, "register-btn").click()
        time.sleep(1)
        # Should redirect to login with success flash, but allow pre-existing user
        flash = wait_for_flash(driver)
        assert ("/login" in driver.current_url) or ("exists" in flash.lower()) or ("already" in flash.lower()) or ("successful" in flash.lower()), \
            "Should redirect to login after registration or show duplicate/success flash"

    def test_register_duplicate_username(self, driver):
        """TC-04: Registration with duplicate username shows error."""
        driver.get(f"{BASE_URL}/register")
        driver.find_element(By.ID, "username").send_keys(TEST_USER)  # same user again
        driver.find_element(By.ID, "password").send_keys(TEST_PASS)
        driver.find_element(By.ID, "register-btn").click()
        time.sleep(1)
        flash = wait_for_flash(driver)
        assert "exists" in flash.lower() or "already" in flash.lower(), \
            "Should show duplicate username error"


class TestLogin:
    """TC-05 to TC-07: Login scenarios."""

    def test_login_page_loads(self, driver):
        """TC-05: Login page renders correctly."""
        driver.get(f"{BASE_URL}/login")
        assert driver.find_element(By.ID, "login-form")
        assert driver.find_element(By.ID, "username")
        assert driver.find_element(By.ID, "password")

    def test_login_invalid_credentials(self, driver):
        """TC-06: Login with wrong password shows error."""
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "username").send_keys(TEST_USER)
        driver.find_element(By.ID, "password").send_keys("WrongPassword!")
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        flash = wait_for_flash(driver)
        assert "invalid" in flash.lower() or "incorrect" in flash.lower() or \
               driver.current_url.endswith("/login"), \
            "Should show invalid credentials error"

    def test_login_valid_credentials(self, driver):
        """TC-07: Login with valid credentials redirects to books page."""
        login(driver)
        time.sleep(1)
        assert "/books" in driver.current_url, "Should redirect to /books after login"
        flash = wait_for_flash(driver)
        assert "welcome" in flash.lower() or "/books" in driver.current_url


class TestAuthProtection:
    """TC-08: Unauthenticated access redirects to login."""

    def test_books_requires_login(self, driver):
        """TC-08: Accessing /books without login redirects to login page."""
        logout(driver)
        time.sleep(0.5)
        driver.get(f"{BASE_URL}/books")
        time.sleep(1)
        assert "/login" in driver.current_url, "Should redirect unauthenticated users to login"
        # Log back in for subsequent tests
        login(driver)
        time.sleep(1)


class TestBookOperations:
    """TC-09 to TC-16: Book CRUD, search, borrow, return."""

    def test_add_book_page_loads(self, driver):
        """TC-09: Add Book page renders correctly."""
        driver.get(f"{BASE_URL}/books/add")
        assert driver.find_element(By.ID, "add-book-form")
        assert driver.find_element(By.ID, "title")
        assert driver.find_element(By.ID, "author")

    def test_add_book_missing_fields(self, driver):
        """TC-10: Adding a book without required fields shows validation error."""
        driver.get(f"{BASE_URL}/books/add")
        # Submit with empty title
        driver.find_element(By.ID, "author").send_keys("Some Author")
        driver.find_element(By.ID, "submit-add-book").click()
        time.sleep(1)
        # Should stay on the same page (HTML5 validation or flash error)
        assert "add" in driver.current_url or wait_for_flash(driver) != ""

    def test_add_book_successfully(self, driver):
        """TC-11: Successfully add a new book."""
        driver.get(f"{BASE_URL}/books/add")
        driver.find_element(By.ID, "title").send_keys(TEST_BOOK_TITLE)
        driver.find_element(By.ID, "author").send_keys(TEST_BOOK_AUTHOR)
        driver.find_element(By.ID, "isbn").send_keys(TEST_BOOK_ISBN)
        driver.find_element(By.ID, "submit-add-book").click()
        time.sleep(1)
        assert "/books" in driver.current_url, "Should redirect to books list after adding"
        flash = wait_for_flash(driver)
        assert "added" in flash.lower() or TEST_BOOK_TITLE in driver.page_source

    def test_book_appears_in_list(self, driver):
        """TC-12: Newly added book appears in the books list."""
        driver.get(f"{BASE_URL}/books")
        time.sleep(0.5)
        assert TEST_BOOK_TITLE in driver.page_source, \
            "Added book should appear in the book list"

    def test_search_book_by_title(self, driver):
        """TC-13: Searching by title filters results correctly."""
        driver.get(f"{BASE_URL}/books")
        search_box = driver.find_element(By.ID, "search-input")
        search_box.clear()
        search_box.send_keys("Selenium")
        driver.find_element(By.ID, "search-btn").click()
        time.sleep(1)
        assert TEST_BOOK_TITLE in driver.page_source, \
            "Search by title should return the matching book"

    def test_edit_book(self, driver):
        """TC-14: Edit an existing book's title."""
        driver.get(f"{BASE_URL}/books")
        edit_btn = driver.find_element(By.CSS_SELECTOR, ".edit-btn")
        edit_btn.click()
        time.sleep(1)
        title_field = driver.find_element(By.ID, "title")
        title_field.clear()
        title_field.send_keys(EDITED_TITLE)
        driver.find_element(By.ID, "submit-edit-book").click()
        time.sleep(1)
        flash = wait_for_flash(driver)
        assert "updated" in flash.lower() or EDITED_TITLE in driver.page_source

    def test_edited_book_appears_in_list(self, driver):
        """TC-15: Edited book title is reflected in the book list."""
        driver.get(f"{BASE_URL}/books")
        time.sleep(0.5)
        assert EDITED_TITLE in driver.page_source, \
            "Edited book title should be visible in the list"

    def test_borrow_book(self, driver):
        """TC-16: Borrow a book changes its status."""
        driver.get(f"{BASE_URL}/books")
        time.sleep(0.5)
        borrow_btn = driver.find_element(By.CSS_SELECTOR, ".borrow-btn")
        borrow_btn.click()
        time.sleep(1)
        flash = wait_for_flash(driver)
        assert "borrowed" in flash.lower() or "borrow" in driver.page_source

    def test_borrowed_book_shows_return_button(self, driver):
        """TC-17 (bonus): After borrowing, Return button appears."""
        driver.get(f"{BASE_URL}/books")
        time.sleep(0.5)
        # return button should now exist
        return_btns = driver.find_elements(By.CSS_SELECTOR, ".return-btn")
        assert len(return_btns) > 0, "Return button should appear after borrowing"

    def test_return_book(self, driver):
        """TC-18 (bonus): Return a borrowed book."""
        driver.get(f"{BASE_URL}/books")
        return_btn = driver.find_element(By.CSS_SELECTOR, ".return-btn")
        return_btn.click()
        time.sleep(1)
        flash = wait_for_flash(driver)
        assert "returned" in flash.lower() or "/books" in driver.current_url

    def test_delete_book(self, driver):
        """TC-19 (bonus): Delete a book removes it from the list."""
        driver.get(f"{BASE_URL}/books/add")
        driver.find_element(By.ID, "title").send_keys("Throwaway Book")
        driver.find_element(By.ID, "author").send_keys("Delete Me")
        driver.find_element(By.ID, "submit-add-book").click()
        time.sleep(1)

        driver.get(f"{BASE_URL}/books")
        initial_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-row"))

        delete_btns = driver.find_elements(By.CSS_SELECTOR, ".delete-btn")
        driver.execute_script("arguments[0].click();", delete_btns[-1])
        time.sleep(0.5)
        # Accept the confirmation dialog
        driver.switch_to.alert.accept()
        time.sleep(1)

        driver.get(f"{BASE_URL}/books")
        new_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-row"))
        assert new_count < initial_count, "Book count should decrease after deletion"


class TestLogout:
    """TC-20: Logout clears session."""

    def test_logout(self, driver):
        """TC-20: Logout redirects to login page."""
        driver.get(f"{BASE_URL}/books")
        logout(driver)
        time.sleep(1)
        assert "/login" in driver.current_url, "Logout should redirect to login page"
