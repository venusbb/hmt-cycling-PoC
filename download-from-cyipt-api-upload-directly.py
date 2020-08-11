
# Purpose: enable download of data for most / all of England from the CyIPT API.
# This is sometimes made difficult by the download limits of the CyIPT API.
# It generally restricts downloads to quite small grid square areas of the UK.

# This script carves up England into these grid square units (about 4000)
# and then programmatically hits the API endpoint for each of these grid squares
# merging the data all into one file in the end.

# References
#
# https://postgis.net/docs/ST_MakePoint.html
#
# http://postgis.refractions.net/documentation/manual-1.5/ST_SRID.html
#
# https://gis.stackexchange.com/questions/68711/postgis-geometry-query-returns-error-operation-on-mixed-srid-geometries-only#68756
#
# https://www.cyipt.bike/api/
#
# https://www.cyipt.bike/#6/53.690/-2.142/mapnik

# import pandas as pd
import numpy as np
import requests
# import pprint as pp
import json, os
from elasticsearch import Elasticsearch


# -------Elastics----------------
CLOUD_ID=os.environ['CLOUD_ID']
API_KEY_1=os.environ['API_KEY_1']
API_KEY_2=os.environ['API_KEY_2']
# Elastic trial account
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=(API_KEY_1,API_KEY_2),
)
print (es.info())

# Proposed cycle_schemes
# index = 'england_cycle_schemes'

# Fatal bike casulties
# incidentType = 'bikeCasFatal'
# index = 'collision_bike_cas_fatal'

# Serious bike casulties
# incidentType = 'bikeCasSerious'
# index = 'collision_bike_cas_serious'

# Slight bike casulties
incidentType = 'bikeCasSlight'
index = 'collision_bike_cas_slight'

mapping = {
    "mappings": {
        "properties": {
            "geometry": {
                "type": "geo_shape" # formerly "string"
            }
        }
    }
}

response = es.indices.create(
    index=index,
    body=mapping,
    ignore=400 # ignore 400 already exists code
)
# end elastics
print(response)


# An approximate bounding box for England in terms of Longitude and Latitude
west = -5.5
east = 2.0
north = 56.0
south = 50.0

# A reliable option for grid square size
# Lower Zoom levels may not return any data.
zoom_level = 13

# A reliable gid square dimension to query over.
# This is small enough that CyIPT doesn't refuse to return.
horizontal_step = 0.18
vertical_step = 0.06

# Segment England into small boxes to query for
num_horizontal_steps = int(np.round((east - west) / horizontal_step))

num_vertical_steps = int(np.round((north - south) / vertical_step))

total_queries = num_horizontal_steps * num_vertical_steps



def write_api_str(wst, sth, est, nth):
    """
    Given the dimensions of the grid square / rect, constructs a
    an request URL to retrieve collision points of given severity
    """
    # Get Cycle cycle_schemes data
    # api_call = (
    #     "https://www.cyipt.bike/api/v1/schemes.json?bbox={w:.2f},{s:.2f},{e:.2f},{n:.2f}&"
    #     "zoom=13&costto=20000000&benefitcostfrom=1"
    # ).format(w=wst, s=sth, e=est, n=nth)

    # Get collision data
    api_call = (
        "https://www.cyipt.bike/api/v1/collisionsroad.geojson?bbox={w:.2f},{s:.2f},{e:.2f},{n:.2f}&"
        "zoom=13&collisionsroadlayer={incidenttype}"
    ).format(w=wst, s=sth, e=est, n=nth, incidenttype=incidentType)



    return api_call


# Assemble all of the API calls into a single list
api_calls = list()

for ix in range(0, num_horizontal_steps):
    wx = west + float(ix) * horizontal_step
    ex = wx + horizontal_step

    for iy in range(0, num_vertical_steps):
        sy = south + float(iy) * vertical_step
        ny = sy + vertical_step

        api_calls.append(
            write_api_str(wx, sy, ex, ny)
        )


for i, api_str in enumerate(api_calls):

    if i % 100 == 0:
        print("{} calls completed".format(i))

    response = requests.get(api_str)
    res = response.json()
    # print(res)
    if 'features' in res:
        map_data = res['features']
        # print(len(map_data))
        for i, md in enumerate(map_data):
            # print(md)
            res = es.index(index=index, ignore=400, body=md, request_timeout=30)
            # print(res)
            if ('result' in res):
                print(res['result'])



print("Complete")
