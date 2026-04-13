import os
from re import search
import shutil
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from app import app
from models import User, db
from tests.test_helpers import (
    cleanup_test_artifacts,
    configure_app_for_tests,
    create_post,
    create_user,
    reset_database,
    LiveServerThread,
    wait_for_server,
)


class SeleniumFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_app_for_tests()
        cls.ctx = app.app_context()
        cls.ctx.push()
        reset_database()
        cls.server = LiveServerThread(app)
        cls.server.start()
        cls.base_url = f'http://127.0.0.1:{cls.server.port}'
        wait_for_server(cls.base_url)
        cls.driver = cls._build_driver()
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        cls.server.shutdown()
        db.session.remove()
        cls.ctx.pop()
        cleanup_test_artifacts()

    @classmethod
    def _build_driver(cls):
        options = Options()
        chrome_bin = os.environ.get('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        elif shutil.which('chromium'):
            options.binary_location = shutil.which('chromium')

        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1440,1080')

        driver_path = os.environ.get('CHROMEDRIVER_PATH')
        try:
            if driver_path:
                return webdriver.Chrome(service=Service(driver_path), options=options)
            return webdriver.Chrome(options=options)
        except NoSuchDriverException as exc:
            raise unittest.SkipTest(
                'Chrome/Chromium WebDriver is not available. '
                'Install chromedriver or set CHROMEDRIVER_PATH before running selenium tests.'
            ) from exc
        except Exception as exc:
            raise unittest.SkipTest(
                f'Could not start Chrome WebDriver for selenium tests: {exc}'
            ) from exc

    def setUp(self):
        reset_database()
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()

    def open(self, path):
        self.driver.get(f'{self.base_url}{path}')

    def login_via_ui(self, email, password='password123'):
        self.open('/login')
        self.wait.until(EC.presence_of_element_located((By.ID, 'login-email'))).send_keys(email)
        self.driver.find_element(By.ID, 'login-password').send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, '#login-form input[type="submit"]').click()
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Log out')))

    def test_register_flow_creates_account(self):
        self.open('/register')

        self.wait.until(
            EC.presence_of_element_located((By.ID, 'reg-username'))
        ).send_keys('newuser')
        self.driver.find_element(By.ID, 'reg-email').send_keys('newuser@student.uwa.edu.au')
        self.driver.find_element(By.ID, 'reg-password').send_keys('Password123!')
        self.driver.find_element(By.ID, 'reg-confirm').send_keys('Password123!')

        submit = self.driver.find_element(
            By.CSS_SELECTOR,
            '#register-form input[type="submit"], #register-form button[type="submit"]'
        )
        submit.click()

        self.wait.until(
            lambda d: 'Log in' in d.page_source or '/login' in d.current_url
        )
        self.assertTrue(
            'Log in' in self.driver.page_source or '/login' in self.driver.current_url
        )

    def test_login_and_logout_flow(self):
        create_user('alice')

        self.login_via_ui('alice@student.uwa.edu.au')
        self.assertIn('Hi, alice', self.driver.page_source)

        self.driver.find_element(By.LINK_TEXT, 'Log out').click()
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Log in')))
        self.assertEqual(self.driver.current_url.rstrip('/'), self.base_url.rstrip('/'))

    def test_dashboard_requires_login_redirects_to_login(self):
        self.open('/dashboard')
        self.wait.until(EC.presence_of_element_located((By.ID, 'login-email')))
        self.assertIn('/login?next=%2Fdashboard', self.driver.current_url)

    def test_create_post_flow_shows_post_on_discovery_and_dashboard(self):
        create_user('poster')
        self.login_via_ui('poster@student.uwa.edu.au')

        self.open('/post/new')
        self.wait.until(EC.presence_of_element_located((By.ID, 'post-title'))).send_keys('Selenium Guitar Lessons')
        Select(self.driver.find_element(By.ID, 'post-category')).select_by_visible_text('Music')
        self.driver.find_element(By.ID, 'post-description').send_keys('I can teach guitar chords and rhythm.')
        self.driver.find_element(By.CSS_SELECTOR, '#post-form input[type="submit"]').click()

        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Selenium Guitar Lessons')))
        self.assertIn('Your skill has been posted!', self.driver.page_source)

        self.open('/dashboard')
        self.wait.until(EC.presence_of_element_located((By.ID, 'pane-posts')))
        self.assertIn('Selenium Guitar Lessons', self.driver.page_source)

    def test_search_returns_matching_post(self):
        user = create_user('searcher')
        create_post(user, title='Japanese conversation practice', category_slug='language')
        create_post(user, title='Beginner Python tutoring', category_slug='coding')

        self.open('/')
        search = self.wait.until(EC.presence_of_element_located((By.ID, 'search-input')))
        search.clear()
        search.send_keys('Japanese')
        self.driver.find_element(By.CSS_SELECTOR, '#search-form button[type="submit"]').click()

        self.wait.until(
            lambda d: 'Japanese conversation practice' in d.find_element(By.ID, 'post-grid').text
        )

        grid_text = self.driver.find_element(By.ID, 'post-grid').text
        self.assertIn('Japanese conversation practice', grid_text)

    def test_owner_cannot_interest_own_post(self):
        owner = create_user('owner')
        post = create_post(owner, title='My own skill listing')
        self.login_via_ui(owner.email)

        self.open(f'/post/{post.id}')
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Edit')))
        self.assertEqual(len(self.driver.find_elements(By.ID, 'interest-btn')), 0)
        self.assertIn('Delete', self.driver.page_source)


if __name__ == '__main__':
    unittest.main()
