from datetime import datetime
from elasticsearch import Elasticsearch
import json, os

CLOUD_ID=os.environ['CLOUD_ID']
API_KEY_1=os.environ['API_KEY_1']
API_KEY_2=os.environ['API_KEY_2']
# Elastic trial account
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=(API_KEY_1,API_KEY_2),
)
print (es.info())

# Change this to upload different datasets to Elastic clusters
load_file = 7

if (load_file == 1):
    # CYIPT Rapid tool cycleway london enriched with cycle length and LA boundary
    filename = 'data/la_boundary_cycle_len_london.json'
    index = 'cycleways_london'

if (load_file == 2):
    # CYIPT Rapid tool cycleway west midlands with cycle length and LA boundary
    filename = 'la_boundary_cycle_len_wm.json'
    index = 'data/cycleways_west_midlands'

if (load_file == 3):
    # CYIPT Rapid tool cycleway london path only
    filename = 'data/cycleways_london.geojson'
    index = 'cycleways_london_paths'

if (load_file == 4):
    # CYIPT Rapid tool cycleway west midlands path only
    filename = 'data/cycleways_west-midlands.geojson'
    index = 'cycleways_west_midland_paths'

if (load_file == 5):
    # Deprivation index by LSOA
    filename = 'data/combine_deprivation.geojson'
    index = 'combine_deprivation'

if (load_file == 6):
    #  Charlie's all metrics in his database dump
    filename = 'data/england_metrics_feature.json'
    index = 'england_metrics_feature'

if (load_file == 7):
    # downloaded directly from CYIPT website for the "schemes" dataset with "download-from-cyipt-api.py" script
    # filename = 'data/england_cycle_schemes.json'
    filename = 'data/test.json'
    index = 'england_cycle_schemes'


# Usage data are uploaded by using Elastic tools

f = open(filename)

docket_content = f.read()

map_content = json.loads(docket_content)

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

# Send the data into es
map_data_json = json.loads(docket_content)
# map_data = map_data.get('features')
# print(map_data_json['features'][0]['geometry'])
map_data = map_data_json['features']

for md in range(1, len(map_data)):
    print(md)
    # print(map_data_json['features'][md])
    res = es.index(index=index, ignore=400, body=map_data[md], request_timeout=30)
    if ('result' in res):
        print(res['result'])

print('exit')
