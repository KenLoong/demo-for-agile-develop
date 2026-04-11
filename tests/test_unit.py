import unittest

from werkzeug.security import check_password_hash

from app import app
from models import db, User, Interest, PostLike
from tests.test_helpers import (
    cleanup_test_artifacts,
    configure_app_for_tests,
    create_interest,
    create_post,
    create_user,
    login,
    reset_database,
)


class UnitRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_app_for_tests()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_artifacts()

    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        reset_database()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

    def test_register_rejects_non_uwa_email(self):
        response = self.client.post(
            '/register',
            data={
                'username': 'invalidemailuser',
                'email': 'invalid@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'submit': 'Sign Up',
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use your UWA student email.', response.data)
        self.assertEqual(User.query.count(), 0)

    def test_register_success_creates_user_with_hashed_password(self):
        response = self.client.post(
            '/register',
            data={
                'username': 'alice',
                'email': 'alice@student.uwa.edu.au',
                'password': 'password123',
                'confirm_password': 'password123',
                'submit': 'Sign Up',
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created! You can now log in.', response.data)
        user = User.query.filter_by(email='alice@student.uwa.edu.au').first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, 'password123')
        self.assertTrue(check_password_hash(user.password_hash, 'password123'))

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard', follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fdashboard', response.headers['Location'])

    def test_cannot_interest_own_post(self):
        owner = create_user('owner')
        post = create_post(owner, title='Own skill')
        login(self.client, owner.email)

        response = self.client.post(f'/interest/{post.id}')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'You cannot request your own skill.')
        self.assertEqual(Interest.query.count(), 0)

    def test_duplicate_interest_is_blocked(self):
        owner = create_user('owner')
        sender = create_user('sender')
        post = create_post(owner, title='Guitar lesson')
        create_interest(sender, post)
        login(self.client, sender.email)

        response = self.client.post(f'/interest/{post.id}')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Already sent a request.')
        self.assertEqual(Interest.query.count(), 1)

    def test_like_toggle_increments_and_decrements_count(self):
        owner = create_user('owner')
        liker = create_user('liker')
        post = create_post(owner, title='French conversation')
        login(self.client, liker.email)

        first = self.client.post(f'/post/{post.id}/like')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()['like_count'], 1)
        self.assertTrue(first.get_json()['liked'])
        self.assertEqual(PostLike.query.count(), 1)

        second = self.client.post(f'/post/{post.id}/like')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.get_json()['like_count'], 0)
        self.assertFalse(second.get_json()['liked'])
        self.assertEqual(PostLike.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
