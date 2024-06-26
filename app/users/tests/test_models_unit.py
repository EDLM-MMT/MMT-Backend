from django.core.exceptions import ValidationError
from django.test import tag

from users.models import (MOS, LowercaseValidator, MMTUser, NumberValidator,
                          SymbolValidator, UppercaseValidator)

from .test_setup import TestSetUp


@tag('unit')
class PasswordValidatorTests(TestSetUp):
    def test_number_validator_success(self):
        """
        Test that number validator passes when it finds numbers
        """

        resp = NumberValidator().validate(password="123")
        self.assertIsNone(resp)

    def test_number_validator_fail(self):
        """
        Test that number validator fails when no numbers
        """
        with self.assertRaises(ValidationError):
            NumberValidator().validate(password="abc")

    def test_number_validator_help(self):
        """
        Test that number validator has help text
        """

        self.assertEqual(NumberValidator().get_help_text(),
                         "Your password must contain at least 1 digit, 0-9.")

    def test_symbol_validator_success(self):
        """
        Test that symbol validator passes when it finds symbol
        """

        resp = SymbolValidator().validate(password="!@#")
        self.assertIsNone(resp)

    def test_symbol_validator_fail(self):
        """
        Test that symbol validator fails when no symbol
        """
        with self.assertRaises(ValidationError):
            SymbolValidator().validate(password="abc")

    def test_symbol_validator_help(self):
        """
        Test that symbol validator has help text
        """

        self.assertEqual(SymbolValidator().get_help_text(
        ), "Your password must contain at least 1 symbol: "
            + "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?")

    def test_lower_validator_success(self):
        """
        Test that lower validator passes when it finds lower
        """

        resp = LowercaseValidator().validate(password="abc")
        self.assertIsNone(resp)

    def test_lower_validator_fail(self):
        """
        Test that lower validator fails when no lower
        """
        with self.assertRaises(ValidationError):
            LowercaseValidator().validate(password="ABC")

    def test_lower_validator_help(self):
        """
        Test that lower validator has help text
        """

        self.assertEqual(LowercaseValidator().get_help_text(
        ), "Your password must contain at least 1 lowercase letter, a-z.")

    def test_upper_validator_success(self):
        """
        Test that upper validator passes when it finds upper
        """

        resp = UppercaseValidator().validate(password="ABC")
        self.assertIsNone(resp)

    def test_upper_validator_fail(self):
        """
        Test that upper validator fails when no upper
        """
        with self.assertRaises(ValidationError):
            UppercaseValidator().validate(password="abc")

    def test_upper_validator_help(self):
        """
        Test that upper validator has help text
        """

        self.assertEqual(UppercaseValidator().get_help_text(
        ), "Your password must contain at least 1 uppercase letter, A-Z.")


@tag('unit')
class MMTUserTests(TestSetUp):
    def test_create_superuser(self):
        """
        Test to make sure superusers are correctly created
        """
        username = "testSuperUser@test.com"
        password = "pass123"
        f_name = "Super"
        l_name = "User"
        su_xdsuser = MMTUser.objects.create_superuser(
            username, password, first_name=f_name, last_name=l_name)

        self.assertEqual(su_xdsuser.email, username.lower())
        self.assertEqual(su_xdsuser.first_name, f_name)
        self.assertEqual(su_xdsuser.last_name, l_name)
        self.assertTrue(su_xdsuser.is_staff)
        self.assertTrue(su_xdsuser.is_active)
        self.assertTrue(su_xdsuser.is_superuser)

    def test_create_user(self):
        """
        Test to make sure users are correctly created
        """
        username = "testUser@test.com"
        password = "pass123"
        f_name = "Basic"
        l_name = "User"
        xdsuser = MMTUser.objects.create_user(
            username, password, first_name=f_name, last_name=l_name)

        self.assertEqual(xdsuser.email, username.lower())
        self.assertEqual(xdsuser.first_name, f_name)
        self.assertEqual(xdsuser.last_name, l_name)
        self.assertFalse(xdsuser.is_staff)
        self.assertTrue(xdsuser.is_active)
        self.assertFalse(xdsuser.is_superuser)


@tag('unit')
class MOSTests(TestSetUp):

    def test_create_mos(self):
        """
        Test to make sure mos are correctly created
        """
        code = "123"
        name = "abc"
        mos = MOS(code=code, name=name)
        mos.save()

        self.assertEqual(mos.code, code)
        self.assertEqual(mos.name, name)
        self.assertIn(code, str(mos))
        self.assertIn(name, str(mos))
