"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_repr(self):
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/warbler-hero.jpg"
        )

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/warbler-hero.jpg"
        )

        db.session.add(u)
        db.session.commit()

        message1 = Message(text="Test message 1", user_id=u.id)
        message2 = Message(text="Test message 2", user_id=u.id)

        db.session.add(message1)
        db.session.add(message2)
        db.session.commit()

        self.assertEqual(len(u.messages), 2)
        self.assertIn(message1, u.messages)
        self.assertIn(message2, u.messages)
        self.assertEqual(len(u.followers), 0)

    def test_user_followers(self):
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD",
            image_url="example1.jpg"
        )

        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD",
            image_url="example2.jpg"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.followers.append(user2)
        db.session.commit()

        self.assertEqual(len(user2.followers), 1)
        self.assertTrue(user2.is_following(user1))

    def test_is_followed_by_true(self):
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD",
            image_url="example1.jpg"
        )

        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD",
            image_url="example2.jpg"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user2.following.append(user1)
        db.session.commit()

        self.assertTrue(user2.is_following(user1))

    def test_user_create_valid_credentials(self):
        user = User.signup(email="test@test.com",
                           username="testuser", password="password123", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()
        self.assertIsNotNone(user.id)

    def test_user_create_invalid_credentials(self):
        User.signup(email="test@test.com", username="testuser",
                    password="password123", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()

        with self.assertRaises(IntegrityError):
            db.session.add(User.signup(email="test@test.com",
                           username="testuser", password="password456", image_url="/static/images/warbler-hero.jpg"))
            db.session.commit()

    def test_user_authenticate_valid_credentials(self):
        User.signup(email="test@test.com", username="testuser",
                    password="password123", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()
        authenticated_user = User.authenticate("testuser", "password123")
        self.assertIsNotNone(authenticated_user)

    def test_user_authenticate_invalid_username(self):
        User.signup(email="test@test.com", username="testuser",
                    password="password123", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()
        authenticated_user = User.authenticate(
            "invalidusername", "password123")
        self.assertIsNone(authenticated_user)

    def test_user_authenticate_invalid_password(self):
        User.signup(email="test@test.com", username="testuser",
                    password="password123", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()
        authenticated_user = User.authenticate("testuser", "wrongpassword")
        self.assertIsNone(authenticated_user)
