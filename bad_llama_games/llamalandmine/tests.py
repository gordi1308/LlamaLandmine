from django.test import TestCase
from django.core.urlresolvers import reverse

from llamalandmine.models import Badge, RegisteredUser, User



class BadgeModelTest(TestCase):

    def setUp(self):
        Badge.objects.create(name="name", description="description")

    def test_badge_unicode_shows_name(self):
        """:returns True if badge__unicode__() returns the name of the badge
        """
        badge = Badge.objects.get(name="name")
        self.assertEqual(badge.__unicode__(), "name")

    def test_badge_default_tier_is_1(self):
        """:returns True if badge.tier is 1 by default
        """
        badge = Badge.objects.get(name="name")
        self.assertEqual(badge.tier, 1)


class RegisteredUserTest(TestCase):

    def setUp(self):
        user = User.objects.create(username="user_test", password="user_pass",
                            email="user@test.com")
        RegisteredUser.objects.create(user=user)

    def test_reguser_unicode_shows_name_capitalize(self):
        user = RegisteredUser.objects.get(user__username="user_test")
        self.assertEqual(user.__unicode__(), "User_test")

    def test_reguser_user_name_shows_name(self):
        user = RegisteredUser.objects.get(user__username="user_test")
        self.assertEqual(user.user_name(), "user_test")

    def test_reguser_user_email_shows_email(self):
        user = RegisteredUser.objects.get(user__username="user_test")
        self.assertEqual(user.user_email(), "user@test.com")


