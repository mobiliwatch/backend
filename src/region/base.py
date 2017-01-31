class Region(object):
    """
    An abstrach region, to be implemented for each case
    """

    def __str__(self):
        return self.__class__.__name__
