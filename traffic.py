from api import Itinisere
import geojson
from geojson import MultiLineString, Feature, FeatureCollection
import re


mline_re = re.compile(r'([\d\.\s,]+)')
mline_re = re.compile('(([\d\., ]+))')

def test():
    api = Itinisere()
    traf = api.get_traffic()


    out = []
    for item in traf['Data']:
        shape_raw = item['Shape']

        # Extract type
        feature = None
        shape_type = shape_raw[:shape_raw.index(' ')]
        if shape_type == 'MULTILINESTRING':
            # Load coords
            coords = shape_raw[len(shape_type)+1:]
            lines = []
            for groups in mline_re.findall(coords):
                line = []
                for couples in map(lambda x : x.split(', '), groups):
                    for couple in couples:
                        try:
                            c = couple.split(' ')
                            lat, lng = float(c[0]), float(c[1])
                            line.append((lat, lng))
                        except:
                            continue
                if line:
                    lines.append(line)
            feature = Feature(geometry=MultiLineString(lines), properties={"type": item['Type']})
            out.append(feature)


    collection = FeatureCollection(out)
    with open('traffic.json', 'w') as f:
        f.write(geojson.dumps(collection))

if __name__ == '__main__':
    test()
