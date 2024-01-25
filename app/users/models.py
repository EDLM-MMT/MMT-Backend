import re

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext as _

from generate_transcript.models import MilitaryCourse

# Create your models here.


class UserRecord(models.Model):
    """Model to store user records"""
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    military_courses = models.ManyToManyField(MilitaryCourse,
                                              related_name="user_record_set")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.email}'


class MMTUserProfileManager(BaseUserManager):
    """User manager"""
    def create_user(self, email, password=None, **other_fields):
        """Create a new user"""
        if not email:
            raise ValueError('Email is required')
        # if not first_name:
        #     raise ValueError('First name is required')
        # if not last_name:
        #     raise ValueError('Last name is required')
        email = email.lower()
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        """Create a super user"""
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')
        user = self.create_user(email, password, **other_fields)
        return user


class MMTUser(AbstractBaseUser, PermissionsMixin):
    """Model to store user login details"""
# User attributes
    username = None
    email = models.EmailField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MMTUserProfileManager()

    def __str__(self):
        return self.email


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 uppercase letter, "
                    "A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 lowercase letter, "
                    "a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\\]{}|\\\\`~!@#$%^&*_\\-+=;:\'",<>./?]',
                          password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"
        )
