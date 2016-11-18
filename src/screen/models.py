from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Location
from django.utils.text import slugify
from datetime import datetime

RATIOS = (
  ('16:9', _('Landscape 16x9')),
  ('9:16', _('Portrait 9x16')),
)

class Screen(models.Model):
    """
    A user screen
    """
    user = models.ForeignKey('users.User', related_name='screens')
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=100)
    ratio = models.CharField(max_length=20, choices=RATIOS, default='16:9')

    class Meta:
        unique_together = (
            ('user', 'slug')
        )

    @property
    def top_groups(self):
        # Used by api
        return self.groups.filter(parent__isnull=True)

    @property
    def frontend_url(self):
        from django.conf import settings
        return settings.FRONTEND_SCREEN_URL.format(self.slug)

    def slugify(self):
        """
        Build a new slug
        """
        assert self.name is not None

        # Try direct django slug
        self.slug = slugify(self.name)
        if not self.user.screens.filter(slug=self.slug).exists():
            return self.slug

        # Iterate over slug
        mask = self.slug + '-%d'
        i = 2
        while True:
            self.slug = mask % i
            if not self.user.screens.filter(slug=self.slug).exists():
                break
            i += 1

        return self.slug

    def build_default_widgets(self, location):
        """
        Build default widgets
        Based on a location
        """
        assert isinstance(location, Location)

        # Init widgets without positions
        loc = LocationWidget(location=location)
        clock = ClockWidget()
        weather = WeatherWidget(city=location.city)
        note = NoteWidget(text='Bienvenue sur Mobili.Watch !')

        if self.ratio == '16:9':
            # Build groups
            left = self.groups.create(position=0, vertical=True)
            right = self.groups.create(position=1, vertical=True)
            right_top = right.groups.create(screen=self, position=0)
            right_bottom = right.groups.create(screen=self, position=1)

            # Location widget on left
            loc.group = left
            loc.save()

            # Clock & Weather on top right
            clock.group = right_top
            clock.save()
            weather.group = right_top
            weather.save()

            # Note below Weather
            note.group = right_bottom
            note.save()

        elif self.ratio == '9:16':
            # Build groups
            top = self.groups.create(screen=self, position=0)
            bottom = self.groups.create(screen=self, position=1)

            # Clock+Weather+Note on top
            clock.group = top
            clock.save()
            weather.group = top
            weather.save()
            note.group = top
            note.save()

            # Location on bottom
            location.group = bottom
            location.save()

class Group(models.Model):
    """
    A group of widget, used for display
    """
    screen = models.ForeignKey(Screen, related_name='groups')
    parent = models.ForeignKey('self', related_name='groups', null=True, blank=True)
    position = models.PositiveIntegerField(default=0)

    vertical = models.BooleanField(default=False)

    class Meta:
        ordering = ('position', )
        unique_together = (
            ('screen', 'parent', 'position'),
        )

    def list_widgets(self):
        """
        List all widgets instances
        Used by API
        """
        return \
            list(self.locationwidget.all()) \
            + list(self.clockwidget.all()) \
            + list(self.weatherwidget.all()) \
            + list(self.notewidget.all())


class Widget(models.Model):
    """
    An abstract widget on a screen
    """
    group = models.ForeignKey(Group, related_name='%(class)s')

    class Meta:
        abstract = True

class ClockWidget(Widget):
    """
    Display clock on a screen
    """
    timezone = models.CharField(max_length=250, default='Europe/Paris')

    def now(self):
        # TODO: use timezone
        return datetime.now()

class LocationWidget(Widget):
    """
    Display location on a screen
    """
    location = models.ForeignKey('users.Location', related_name='widgets')

    def get_size(self):
        w, h = self.screen.size
        if self.screen.ratio == '16:9':
            return (w / 2, h)
        if self.screen.ratio == '9:16':
            return (w, h / 2)

class WeatherWidget(Widget):
    """
    Display current weather on a screen
    """
    city = models.ForeignKey('transport.City', related_name='weather_widgets')

    def get_weather(self):
        # TODO
        return 'sunny'

class NoteWidget(Widget):
    """
    Display some text on a screen
    """
    text = models.TextField()
