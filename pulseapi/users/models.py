from django.db import models

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)

from pulseapi.profiles.models import UserProfile


class EmailUserManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        if not name:
            raise ValueError('Users must have a name')

        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            password = self.make_random_password()

        # Ensure that new users get a user profile associated
        # with them, even though it'll be empty by default.
        profile = UserProfile.objects.create(is_active=True)
        user = self.model(
            email=email,
            name=name,
            profile=profile,
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, name, email, password):
        user = self.create_user(
            name=name,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class EmailUser(AbstractBaseUser, PermissionsMixin):
    # We treat the user's email address as their username
    email = models.CharField(
        verbose_name='email (acts as username)',
        max_length=254,
        unique=True,
    )

    # And we have an additional field for the user's full name,
    # as Django's User model is not useful for world users.
    name = models.CharField(max_length=1000)

    # Is this user a valid Django administrator?
    is_staff = models.BooleanField(
        default=False,
        verbose_name="this user counts as django::staff",
    )

    # A user can have only zero or one profile. For social auth, the profile is
    # automatically created for the user.
    profile = models.OneToOneField(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='related_user',
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = EmailUserManager()

    def get_full_name(self):
        return self.name + " (" + self.email + ")"

    def get_short_name(self):
        return self.email

    def clean(self):
        pass

    def toString(self):
        return self.email

    def __unicode__(self):
        return self.toString()

    def __str__(self):
        return self.toString()
