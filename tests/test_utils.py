"""Тесты вспомогательных функций (валидация email)."""

import unittest

from utils import is_valid_email


class TestEmailValidation(unittest.TestCase):
    def test_valid_emails(self) -> None:
        self.assertTrue(is_valid_email("ivan.petrov@novasoft.local"))
        self.assertTrue(is_valid_email("a@b.co"))

    def test_invalid_emails(self) -> None:
        self.assertFalse(is_valid_email(""))
        self.assertFalse(is_valid_email("not-an-email"))
        self.assertFalse(is_valid_email("@nodomain.com"))
        self.assertFalse(is_valid_email("spaces in@mail.com"))
        self.assertFalse(is_valid_email("double@@mail.com"))
