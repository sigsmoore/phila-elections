# merge the "Political Wards" and "Political Divisions" geojson files

import json

with open('data.geo/Phila_Political_Wards.geojson') as f:
    geo_ward = json.load(f)
with open('data.geo/Phila_Political_Divisions.geojson') as f:
    geo_div = json.load(f)

def merge_geojson(g1, k1, g2, k2, name):
    assert g1['type'] == g2['type'] and g1['crs'] == g2['crs']
    features = []
    for ft in g1['features']:
        ft['id'] = ft['id'] if k1 is None else ft['properties'][k1]
        features.append(ft)
    for ft in g2['features']:
        ft['id'] = ft['id'] if k2 is None else ft['properties'][k2]
        features.append(ft)
    return dict(
        name=name,
        type=g1['type'],
        crs=g1['crs'],
        features=features,
    )

geo = merge_geojson(geo_ward, 'WARD_NUM', geo_div, 'DIVISION_NUM', 'Philadelphia Political Divisions')

with open('data.geo/Phila_Political_Merged.geojson', 'w') as f:
    json.dump(geo, f)
