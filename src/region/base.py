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
