from django.contrib.gis.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from providers import Router
from region.models import RegionModel
import logging


logger = logging.getLogger('users.models')


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Twitter authentication
    twitter_token = models.CharField(max_length=250, null=True, blank=True)
    twitter_secret = models.CharField(max_length=250, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def has_twitter_auth(self):
        """
        Helper to check if user has twitter credentials
        """
        return self.twitter_token is not None \
            and self.twitter_secret is not None

class Location(RegionModel):
    """
    A location for a user
    Attached to a region
    """
    user = models.ForeignKey(User, related_name='locations')
    name = models.CharField(max_length=250)
    address = models.TextField()
    city = models.ForeignKey('region.City', related_name='locations')
    point = models.PointField()

    line_stops = models.ManyToManyField('transport.LineStop', through='users.LocationStop', related_name='locations')

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} : {} - {}'.format(self.name, self.address, self.city)

    @property
    def screens(self):
        # Used by API
        from screen.models import Screen
        return Screen.objects.filter(groups__locationwidget__location=self)

class LocationStop(models.Model):
    """
    Link a location and a line stop
    """
    location = models.ForeignKey(Location, related_name='location_stops')
    line_stop = models.ForeignKey('transport.LineStop', related_name='location_stops')

    # Link metadata
    distance = models.FloatField(default=0)
    walking_time = models.FloatField(default=0) # as seconds

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('location', 'line_stop'),
        )

    def update_metadata(self):
        """
        Update distance & walking time in here
        """
        try:
            router = Router()
            trip = router.walk_trip(self.location.point, self.line_stop.point)
        except Exception as e:
            logger.error('Failed to updated LocationStop #{} : {}'.format(self.id, e))
            return

        self.distance = trip['distance']
        self.walking_time = trip['duration']
        logger.info('Update location stop #{} with distance={} time={}'.format(self.id, self.distance, self.walking_time))

