from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Location
from django.utils.text import slugify
from channels import Group as WsGroup
import uuid
import time
import json
from datetime import datetime
from django.utils.timezone import utc
import calendar

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
    token = models.UUIDField(default=uuid.uuid4)

    active = models.BooleanField(default=False) # triggered by WS

    class Meta:
        unique_together = (
            ('user', 'slug'),
            ('slug', 'token'),
        )

    def __str__(self):
        return self.name

    @property
    def top_groups(self):
        # Used by api
        return self.groups.filter(parent__isnull=True)

    @property
    def ws_group(self):
        # Used by websockets
        return WsGroup('screen_{}'.format(self.id))

    @property
    def all_widgets(self):
        # Used by api
        return [w for g in self.groups.all() for w in g.list_widgets()]

    @property
    def frontend_url(self):
        from django.conf import settings
        return settings.FRONTEND_SCREEN_URL.format(self.slug)

    @property
    def frontend_shared_url(self):
        from django.conf import settings
        return settings.FRONTEND_SCREEN_SHARED_URL.format(self.slug, self.token)

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
            base = self.groups.create(screen=self, vertical=True, position=0)
            top = base.groups.create(screen=self, position=0)
            bottom = base.groups.create(screen=self, position=1)

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group = models.ForeignKey(Group, related_name='%(class)s')

    class Meta:
        abstract = True

    def send_ws_update(self, extra_data=None):
        """
        Send an update to screens through WebSockets
        """
        # Build update data
        update = self.build_update()
        print('sending', update)

        # Get utc now
        now = datetime.utcnow().replace(tzinfo=utc)
        t = calendar.timegm(now.timetuple())

        if isinstance(extra_data, dict):
            update.update(extra_data)
        data = {
            'time' : t,
            'widget': str(self.id),
            'update': update,
        }

        # Send to WebSocket group
        # as json on text
        self.group.screen.ws_group.send({
            'text' : json.dumps(data)
        })

    def build_update(self):
        """
        Implemented in sub classes
        """
        raise NotImplementedError

class ClockWidget(Widget):
    """
    Display clock on a screen
    """
    timezone = models.CharField(max_length=250, default='Europe/Paris')

    def now(self):
        """
        As timestamp !
        """
        # TODO: use timezone
        return time.time()

    def build_update(self):
        """
        Send date to screens
        """
        return {
            'now' : self.now(),
        }

class LocationWidget(Widget):
    """
    Display location on a screen
    """
    location = models.ForeignKey('users.Location', related_name='widgets')

    def build_update(self):
        """
        Send next times to screens
        """
        from api.serializers import LineStopSerializer

        def _serialize(ls):

            # Start from line stop
            out = LineStopSerializer(ls.line_stop).data

            # Add trip metadata
            out['stop'].update({
                'distance' : ls.distance,
                'walking_time' : ls.walking_time,
            })

            # Add times
            out['times'] = ls.line_stop.get_next_times()
            return out

        return {
            'location' : {
                'line_stops' : [_serialize(ls) for ls in self.location.location_stops.all()]
            },
        }


class WeatherWidget(Widget):
    """
    Display current weather on a screen
    """
    city = models.ForeignKey('transport.City', related_name='weather_widgets')

    def build_update(self):
        """
        Send weather to screens
        """
        weather = self.city.get_weather()
        return {
            'observed' : weather.get_reference_time(),
            'wind' : weather.get_wind(),
            'humidity' : weather.get_humidity(),
            'temperature' : weather.get_temperature(unit='celsius'),
            'status' : weather.get_status(),
            'code' : weather.get_weather_code(),
            'sunrise' : weather.get_sunrise_time(),
            'sunset' : weather.get_sunset_time(),
        }

class NoteWidget(Widget):
    """
    Display some text on a screen
    """
    text = models.TextField()

    def build_update(self):
        """
        Send text to screens
        """
        return {
            'text' : self.text,
        }
