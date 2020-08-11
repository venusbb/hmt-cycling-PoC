# download Charlie's metric feature into a json file
ogr2ogr -f "GeoJSON" ./england_metrics_feature.json PG:"dbname=cb_data" -sql "select * from public.la_metrics_feature"
