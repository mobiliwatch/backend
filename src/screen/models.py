from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from rest_framework.renderers import JSONRenderer
from PIL import Image, ImageDraw
from providers import Twitter
from channels import Group as WsGroup
import uuid
import time
import json
import arrow
from io import BytesIO
from datetime import datetime
from django.utils.timezone import utc
import calendar

STYLES = (
    ('light', _('Light')),
    ('dark', _('Dark')),
)

class Screen(models.Model):
    """
    A user screen
    """
    user = models.ForeignKey('users.User', related_name='screens', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=100)
    style = models.CharField(max_length=10, choices=STYLES, default='light')
    token = models.UUIDField(default=uuid.uuid4)
    is_template = models.BooleanField(default=False)

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

    def clone_widgets(self, screen, location=None):
        """
        Build initial widgets
        Based on an existing screen, by cloning their type
        and not their property
        """
        assert isinstance(screen, Screen)

        # Get a location
        if location is None:
            location = self.user.locations.last()
            if location is None:
                raise Exception('Missing location')

        # Check we have no groups
        if self.groups.exists():
            raise Exception('Screen not empty')

        def _clone_widget(widget):
            cls = widget.__class__
            w = cls()
            if isinstance(w, LocationWidget) or isinstance(w, DisruptionWidget):
                w.location = location
            elif isinstance(w, WeatherWidget):
                w.city = location.city
            elif isinstance(w, NoteWidget):
                w.text = widget.text
            return w

        def _clone_groups(groups, parent=None):

            for group_src in groups:
                # Create a new group
                data = {
                    'parent': parent,
                    'position': group_src.position,
                    'vertical': group_src.vertical,
                }
                group = self.groups.create(**data)

                # Clone all widgets
                for w_src in group_src.list_widgets():
                    w = _clone_widget(w_src)
                    w.position = w_src.position
                    w.group = group
                    w.save()

                # Recurse
                _clone_groups(group_src.groups.all(), group)

        _clone_groups(screen.groups.filter(parent__isnull=True))

    @property
    def preview_key(self):
        return 'screen:preview:{}'.format(self.id)

    def get_preview(self):
        """
        Fetch preview from cache or build a new one
        """
        out = cache.get(self.preview_key)
        if out is None:
            out = self.build_preview()
        return out

    def build_preview(self, width=320, height=180):
        """
        Build an image preview
        """
        padding = 2
        widget_color = '#3273dc'
        group_color = '#888888'

        def _draw_groups(groups, widgets, box, vertical=False):

            objects = list(groups) + list(widgets)
            nb = len(objects)
            if not nb:
                return

            left, top, right, bottom = box

            # Divide horizontally ?
            w = vertical and (right-left) or (right-left) / nb
            h = vertical and (bottom-top) / nb or (bottom-top)
            for i, obj in enumerate(objects):
                x = (not vertical and i*w or 0) + left
                y = (vertical and i*h or 0) + top
                box = (x+padding, y+padding, x+w-padding, y+h-padding)

                if isinstance(obj, Group):
                    # Outline groups
                    draw.rectangle(box, outline=group_color)

                    # Recurse
                    _draw_groups(obj.groups.all(), obj.list_widgets(), box, obj.vertical)
                else:
                    # Fill widgets
                    draw.rectangle(box, fill=widget_color)

        # Init draw
        img = Image.new('RGBA', (width, height), (255,255,255,0))
        draw = ImageDraw.Draw(img)

        # Draw all
        top_groups = self.groups.filter(parent__isnull=True)
        _draw_groups(top_groups, [], (0, 0, width, height))

        # Store in cache, it's really lightweiight (<1kb)
        output = BytesIO()
        img.save(output, format='PNG')
        contents = output.getvalue()
        output.close()
        cache.set(self.preview_key, contents, 12*3600)

        return contents


    def send_ws_update(self):
        """
        Send an update to screens through WebSockets
        """
        from api.serializers import ScreenSerializer
        serializer = ScreenSerializer(instance=self)
        data = {
            'type' : 'screen',
            'update' : serializer.data,
        }
        self.ws_group.send({
            'text' : JSONRenderer().render(data).decode('utf-8')
        })

class Group(models.Model):
    """
    A group of widget, used for display
    """
    screen = models.ForeignKey(Screen, related_name='groups', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='groups', null=True, blank=True, on_delete=models.CASCADE)
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
        all_widgets = list(self.locationwidget.all()) \
            + list(self.clockwidget.all()) \
            + list(self.weatherwidget.all()) \
            + list(self.notewidget.all()) \
            + list(self.twitterwidget.all()) \
            + list(self.disruptionwidget.all())
        return sorted(all_widgets, key=lambda w: w.position)


class Widget(models.Model):
    """
    An abstract widget on a screen
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group = models.ForeignKey(Group, related_name='%(class)s', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)


    class Meta:
        abstract = True
        ordering = ('group', 'position')
        unique_together = (
            ('group', 'position'),
        )

    def send_ws_update(self, extra_data=None):
        """
        Send an update to screens through WebSockets
        """
        # Build update data
        update = self.build_update()

        # Get utc now
        now = datetime.utcnow().replace(tzinfo=utc)
        t = calendar.timegm(now.timetuple())

        if isinstance(extra_data, dict):
            update.update(extra_data)
        data = {
            'type' : 'widget',
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
    location = models.ForeignKey('users.Location', related_name='widgets', on_delete=models.CASCADE)
    auto_pagination = models.BooleanField(default=False)

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

                # Calc bounds around walking time
                'walking_min_time' : ls.walking_time * 0.8,
                'walking_max_time' : ls.walking_time * 1.2,
            })

            # Add times
            out['times'] = ls.line_stop.get_next_times()
            return out

        return {
            'auto_pagination' : self.auto_pagination,
            'location' : {
                'line_stops' : [_serialize(ls) for ls in self.location.location_stops.all()]
            },
        }


class WeatherWidget(Widget):
    """
    Display current weather on a screen
    """
    city = models.ForeignKey('region.City', related_name='weather_widgets', on_delete=models.CASCADE)

    def build_update(self):
        """
        Send weather to screens
        """

        # Load weather
        weather = self.city.get_weather()

        # Load air quality
        air_quality = self.city.get_air_quality()

        return {
            'city' : {
                'name' : self.city.name,
            },
            'observed' : weather.get_reference_time(),
            'wind' : weather.get_wind(),
            'humidity' : weather.get_humidity(),
            'temperature' : weather.get_temperature(unit='celsius'),
            'status' : weather.get_status(),
            'code' : weather.get_weather_code(),
            'sunrise' : weather.get_sunrise_time(),
            'sunset' : weather.get_sunset_time(),
            'air_quality' : air_quality,
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

class DisruptionWidget(Widget):
    """
    List active disruptions for a location
    """
    location = models.ForeignKey('users.Location', related_name='widgets_disruptions', on_delete=models.CASCADE)

    def build_update(self):
        """
        Send active disruptions
        """

        # All disruptions, linearized
        disruptions = sum([ls.direction.get_disruptions() for ls in self.location.line_stops.all()], [])

        # Unique disruptions
        seen = set()
        disruptions = [seen.add(d['id']) or d for d in disruptions if d['id'] not in seen]

        # Sort by date
        disruptions = sorted(disruptions, key=lambda d : d['start'], reverse=True)

        return {
            'disruptions' : list(disruptions),
        }


TWITTER_MODES = (
    ('timeline', _('Timeline')),
    ('user_tweets', _('User Tweets')),
    ('search', _('Search')),
)

class TwitterWidget(Widget):
    """
    Display a twitter feed on a widget
    """
    mode = models.CharField(max_length=50, choices=TWITTER_MODES, default='timeline')
    search_terms = models.CharField(max_length=250, null=True, blank=True)

    def build_update(self):
        """
        Send tweets according to mode
        """
        tw = Twitter(self.group.screen.user)
        if self.mode == 'timeline':
            tweets = tw.timeline()
        elif self.mode == 'user_tweets':
            tweets = tw.user_tweets()
        elif self.mode == 'search':
            if not self.search_terms:
                raise Exception('Missing twitter search terms')
            tweets = tw.search(self.search_terms)
        else:
            raise Exception('Invalid twitter mode')

        def _serialize(tweet):
            # TODO: display photos... maybe ?
            if False and tweet.media:
                photos = [m.media_url_https for m in tweet.media if m.type == 'photo']
            else:
                photos = []
            date_format = 'ddd MMM DD HH:mm:ss Z YYYY'
            return {
                'id': tweet.id,
                'user': tweet.user.screen_name,
                'fullname': tweet.user.name,
                'avatar': tweet.user.profile_image_url,
                'created': arrow.get(tweet.created_at, date_format).timestamp,
                'text': tweet.text,
                'photos': photos,
            }

        return {
            'mode': self.mode,
            'search_terms': self.search_terms,
            'tweets': [_serialize(t) for t in tweets],
        }
