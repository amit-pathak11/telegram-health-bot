from unittest import TestCase

from utils.helper import check_age, check_name, check_gender


class TestAge(TestCase):
    def test_age(self):
        self.assertTrue(check_age('18'))
        self.assertFalse(check_age('abc'))
        self.assertTrue(check_age(50))

    def test_do_not_allow_minors(self):
        self.assertFalse(check_age('4'))


class TestName(TestCase):
    def test_name(self):
        self.assertTrue(check_name('John'))

    def test_name_check_numbers(self):
        self.assertFalse(check_name('Abc234'))

    def test_name_check_spaces(self):
        self.assertFalse(check_name('abc xyz'))


class TestGender(TestCase):
    def test_gender(self):
        self.assertFalse(check_gender('male'))

    def test_gender_emoji(self):
        self.assertTrue(check_gender('Male 👨🏻'))
