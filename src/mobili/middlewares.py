from django.conf import settings


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']

        return self.get_response(request)

def version(request):
    """
    Add version from settings to every template context
    """
    return {
        'VERSION' : settings.VERSION,
    }
