import os
import json


annotations = json.load(open("via_region_data.json"))
annotations = list(annotations.values())

annotations = [a for a in annotations if a['regions']]

#print(annotations)

# Add images
for a in annotations:
    # Get the x, y coordinaets of points of the polygons that make up
    # the outline of each object instance. These are stores in the
    # shape_attributes (see json format above)
    # The if condition is needed to support VIA versions 1.x and 2.x.

    print(a['filename'])

    if type(a['regions']) is dict:
        polygons = [r['shape_attributes'] for r in a['regions'].values()]
        custom = [s['region_attributes'] for s in a['regions'].values()]
    else:
        polygons = [r['shape_attributes'] for r in a['regions']]
        custom = [s['region_attributes'] for s in a['regions']]

    for i,p in enumerate(polygons):
        print(p['all_points_y'])
        print(p['all_points_x'])

    for n in custom:
        print(n['custom'])
    print('----------------------')