from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Location
from django.utils.text import slugify

RATIOS = (
  # Gets 8x2 blocks
  ('16:9', _('Landscape 16x9')),
  # Gets 2x8 blocks
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

    @property
    def size(self):
        # In blocks
        if self.ratio == '16:9':
            return (8, 2)
        if self.ratio == '9:16':
            return (2, 8)

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

    def build_default_widgets(self, location):
        """
        Build default widgets
        Based on a location
        """
        assert isinstance(location, Location)

        # Init widgets without positions
        loc = LocationWidget(screen=self, location=location)
        clock = ClockWidget(screen=self)
        weather = WeatherWidget(screen=self, city=location.city)
        note = NoteWidget(screen=self, text='Bienvenue sur Mobili.Watch !')

        if self.ratio == '16:9':
            # Location widget on left
            loc.top, loc.left = 0, 0
            loc.save()

            # Clock on top right
            clock.top, clock.left = 0, self.size[0] - 1
            clock.save()

            # Weather below clock
            weather.set_below(clock)
            weather.save()

            # Note below Weather
            note.set_below(weather)
            note.save()

        elif self.ratio == '9:16':

            # Clock on top
            clock.top, clock.left = 0, 0
            clock.save()

            # Weather next to clock
            weather.set_next(clock)
            weather.save()

            # Location below clock
            location.set_below(clock)
            location.save()

            # Note below location
            note.set_below(weather)
            weather.save()

        # TODO: check integrity

class Widget(models.Model):
    """
    An abstract widget on a screen
    """
    screen = models.ForeignKey(Screen, related_name='%(class)s')

    # Position
    top = models.PositiveIntegerField()
    left = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def build_payload(self):
        raise NotImplementedError

    @property
    def size(self):
        return self.get_size()

    def get_size(self):
        # default size in blocks
        return (1, 1)

    @property
    def bottom(self):
        return self.top + self.size[1]

    @property
    def right(self):
        return self.left + self.size[0]

    def set_next(self, widget):
        """
        Calc new position for widget
        on the right of specified one
        """
        self.top = widget.top
        self.left = widget.right

    def set_below(self, widget):
        """
        Calc new position for widget
        on the bottom of specified one
        """
        self.top = widget.bottom
        self.left = widget.left


class ClockWidget(Widget):
    """
    Display clock on a screen
    """
    timezone = models.CharField(max_length=250, default='Europe/Paris')

    def build_payload(self):
        """
        Current timestamp
        """
        import time
        return {
            'time' : time.time(),
        }

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

    def build_payload(self):
        return {}

class WeatherWidget(Widget):
    """
    Display current weather on a screen
    """
    city = models.ForeignKey('transport.City', related_name='weather_widgets')

    def build_payload(self):
        # TODO
        return {}


class NoteWidget(Widget):
    """
    Display some text on a screen
    """
    text = models.TextField()

    def build_payload(self):
        # TODO
        return {
            'text' : self.text,
        }
