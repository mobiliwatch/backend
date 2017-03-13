class Region(object):
    """
    An abstrach region, to be implemented for each case
    """

    def __str__(self):
        return self.__class__.__name__

    def list_lines(self):
        """
        List lines on provider to build them in DB later on
        """
        raise NotImplementedError

    def build_line(self, data):
        """
        Build a line in DB from its base data on provider
        """
        raise NotImplementedError

    def build_stops(self, line, data):
        """
        Build all line stops in DB from its base data on provider
        and the line instance
        """
        raise NotImplementedError

    def build_cache(self, widget_type):
        """
        Build an optional cache for a widget type
        """
        raise NotImplementedError

    def next_times(self, line_stop):
        """
        Get stop hours for a line stop instance
        and direction using region providers
        """
        raise NotImplementedError

    def find_stops(self, location, distance):
        """
        Find stops near a location, under a given distance
        """
        raise NotImplementedError

    def list_disruptions(self, direction):
        """
        Load disruptions about a specified direction
        """
        raise NotImplementedError
