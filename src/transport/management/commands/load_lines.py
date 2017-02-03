from django.core.management.base import BaseCommand
import region
from pprint import pprint


class Command(BaseCommand):
    help = 'Setup transport lines'

    def add_arguments(self, parser):
        parser.add_argument('region', help='Target region slug')
        parser.add_argument('--with-stops', dest='with_stops', default=False, action='store_true')

    def handle(self, *args, **options):

        # Load region
        r = region.get(options['region'])
        for line_data in r.list_lines():
            try:
                line = r.build_line(line_data)
                print(line)
                if options['with_stops']:
                    r.build_stops(line, line_data)
            except Exception as e:
                print('ERROR: {}'.format(e))
                pprint(line_data)
