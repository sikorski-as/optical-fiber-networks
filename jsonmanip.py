import json
from pprint import pprint


def load_from_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data


def load_geojson(a3_code):
    return load_from_file(f'data/countries/data/{a3_code.lower()}.geo.json')


def get_countries_db():
    countries = load_from_file('data/countries/countries.json')

    a2_mappings = {}
    a3_mappings = {}
    for i, c in enumerate(countries):
        a2_mappings[c['cca2']] = i
        a3_mappings[c['cca3']] = i
        c['geo'] = load_geojson(c['cca3'])

    return countries, a2_mappings, a3_mappings


def filter_countries(countries, a2_map, a3_map, filter_func):
    filtered = list(filter(filter_func, countries))
    new_a2_map = {}
    new_a3_map = {}

    for i, c in enumerate(filtered):
        new_a2_map[c['cca2']] = i
        new_a3_map[c['cca3']] = i

    return filtered, new_a2_map, new_a3_map


def get_features(geojson_object):
    return geojson_object['features']


def get_list_of_polygons(feature):
    if not 'geometry' in feature:
        return []

    if feature['geometry']['type'] == 'Polygon':
        return feature['geometry']['coordinates']
    elif feature['geometry']['type'] == 'MultiPolygon':
        list = []
        for pol in feature['geometry']['coordinates']:
            list.append(pol[0])
        return list
