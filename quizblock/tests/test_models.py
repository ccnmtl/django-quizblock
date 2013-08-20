from django.test import TestCase
from quizblock.models import Quiz


class TestBasics(TestCase):
    def test_create(self):
        q = Quiz()
        self.assertNotEqual(q, None)

    def test_needs_submit(self):
        q = Quiz()
        self.assertTrue(q.needs_submit())
        q.rhetorical = True
        self.assertFalse(q.needs_submit())
