from arcgis.gis import GIS
from arcgis.mapping import WebMap

#gis = GIS("https://earl.esri.com/portal", "siteadmin", "siteadmin", verify_cert=False)
#print("Successfully Logged Into GIS: ", gis)

data_ = {
	"operationalLayers": [{
			"id": "layer_2382",
			"layerType": "ArcGISMapServiceLayer",
			"url": "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer",
			"visibility": True,
			"opacity": 1,
			"title": "Census Data",
			"layers": [{
					"id": 0,
					"layerDefinition": {
						"source": {
							"type": "mapLayer",
							"mapLayerId": 0
						}
					},
					"name": "Census Block Points",
					"minScale": 99999.99998945338,
					"maxScale": 0,
					"parentLayerId": -1,
					"defaultVisibility": True
				}, {
					"id": 1,
					"layerDefinition": {
						"source": {
							"type": "mapLayer",
							"mapLayerId": 1
						},
						"drawingInfo": {
							"renderer": {
								"type": "simple",
								"label": "",
								"description": "",
								"symbol": {
									"color": [0, 0, 0, 0],
									"outline": {
										"color": [230, 230, 0, 255],
										"width": 0.39975000000000005,
										"type": "esriSLS",
										"style": "esriSLSSolid"
									},
									"type": "esriSFS",
									"style": "esriSFSSolid"
								}
							}
						}
					},
					"name": "Census Block Group",
					"minScale": 1000000,
					"maxScale": 0,
					"parentLayerId": -1,
					"defaultVisibility": True
				}, {
					"id": 2,
					"layerDefinition": {
						"source": {
							"type": "mapLayer",
							"mapLayerId": 2
						},
						"drawingInfo": {
							"renderer": {
								"type": "simple",
								"label": "",
								"description": "",
								"symbol": {
									"color": [0, 0, 0, 0],
									"outline": {
										"color": [230, 230, 0, 255],
										"width": 0.5625,
										"type": "esriSLS",
										"style": "esriSLSSolid"
									},
									"type": "esriSFS",
									"style": "esriSFSSolid"
								}
							}
						}
					},
					"name": "Detailed Counties",
					"minScale": 0,
					"maxScale": 0,
					"parentLayerId": -1,
					"defaultVisibility": True
				}, {
					"id": 3,
					"layerDefinition": {
						"source": {
							"type": "mapLayer",
							"mapLayerId": 3
						},
						"drawingInfo": {
							"renderer": {
								"type": "simple",
								"label": "",
								"description": "",
								"symbol": {
									"color": [0, 0, 0, 0],
									"outline": {
										"color": [230, 230, 0, 255],
										"width": 2,
										"type": "esriSLS",
										"style": "esriSLSSolid"
									},
									"type": "esriSFS",
									"style": "esriSFSSolid"
								}
							}
						}
					},
					"name": "states",
					"minScale": 0,
					"maxScale": 0,
					"parentLayerId": -1,
					"defaultVisibility": True
				}
			]
		}
	],

	"baseMap": {
		"baseMapLayers": [{
				"id": "labels",
				"layerType": "ArcGISTiledMapServiceLayer",
				"url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer",
				"visibility": True,
				"opacity": 1,
				"title": "World_Dark_Gray_Base"
			}, {
				"id": "base",
				"layerType": "ArcGISTiledMapServiceLayer",
				"url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Reference/MapServer",
				"visibility": True,
				"opacity": 1,
				"title": "World_Dark_Gray_Reference"
			}
		],
		"title": "Basemap"
	},
	"spatialReference": {
		"wkid": 102100,
		"latestWkid": 3857
	},
	"authoringApp": "WebMapViewer",
	"authoringAppVersion": "10.6.1",
	"version": "2.11"
}

#item_properties_dict = {"type": "Web Map",
#                        "title": "Test Map",
#                        "tags": ["test", "test1", "test2"],
#                        "snippet": "This is a snippet",
#                        "text": data}
#
#newmap = gis.content.add(item_properties=item_properties_dict)

from arcgis import GIS
import json, sys


def search_layer(conn, layer_name):
	search_results = conn.content.search(layer_name, item_type='*')
	proper_index = [i for i, s in enumerate(search_results) if '"' + layer_name + '"' in str(s)]
	found_item = search_results[0]#[proper_index[0]]
	get_item = conn.content.get(found_item.id)
	return get_item


def update_layer_def(item):
	item_data = item.get_data()

	if item_data is not None:

		# Here note we are changing a specific part of the Layer Definition
		layer_def = item_data['layers'][0]['layerDefinition']
		print("*******************ORIGINAL DEFINITION*********************")
		print(json.dumps(item_data, indent=4, sort_keys=True))

		# Open JSON file containing symbology update
		#with open('/path/to/drawingInfo.json') as json_data:
		#	data = json.load(json_data)
		data = data_['operationalLayers'][0]['layers'][2]['layerDefinition']['drawingInfo']
		print(data)

		# Set the drawingInfo equal to what is in JSON file
		layer_def['drawingInfo'] = data

		# Set the item_properties to include the desired update
		item_properties = {"text": json.dumps(item_data)}

		# 'Commit' the updates to the Item
		item.update(item_properties=item_properties)

		# Print item_data to see that changes are reflected
		new_item_data = item.get_data()
		print("***********************NEW DEFINITION**********************")
		print(json.dumps(new_item_data, indent=4, sort_keys=True))

	else:

		print("There is no Layer Definition at the moment..creating one...")
		create_layer_def(item)


def create_layer_def(item):
	with open('/path/to/complete.json') as json_data:
		data = json.load(json_data)

	# Set the item_properties to include the desired update
	item_properties = {"text": json.dumps(data)}

	# 'Commit' the updates to the Item
	item.update(item_properties=item_properties)

	# Print item_data to see that changes are reflected
	item_data = item.get_data()
	print("*********************CREATED DEFINITION************************")
	print(json.dumps(item_data, indent=4, sort_keys=True))


def main():
	conn = GIS('https://meiamerica.maps.arcgis.com/', 'chigham_mei', 'Kingchr23!')  # Search for item, get item data)
	item = search_layer(conn, 'Grade check observations')
	map_json_dict = item.get_data()

	# Add missing data to the dictionary
	map_json_dict["mapOptions"] = {"extent": {"xmin": -12550000, "ymin": 4850000, "xmax": -12350000, "ymax": 5000000, "spatialReference": {"wkid": 3857}}}
	map_json_dict["exportOptions"] = {"dpi": 50, "outputSize": [1500, 900]}
	#from copy import copy
	#map_json_dict["operationalLayers"] = [{"layers": copy(map_json_dict["layers"])}]
	#del map_json_dict["layers"]
	map_json_dict["operationalLayers"] = [
		{
			#"url": "https://services5.arcgis.com/mvnrDxfOCq0CsVom/arcgis/rest/services/Grade_check_observations/FeatureServer/0",
			#"title": "Point layer",
			#"opacity": 1,
			"layerType": "ArcGISFeatureLayer",
			"id": "mapNotes_2391",
			"title": "Feature Collection - Map Notes",
			"featureCollectionType": "notes",
			"featureCollection": {
				"layers": [],
				"showLegend": False
			},
			"opacity": 1,
			"visibility": True
		}
	]
	map_json_dict["operationalLayers"][0]["layerDefinition"] = {
		"definitionExpression": grade_query_string(),
		"drawingInfo": {
			"renderer": {
				'description': '',
				'label': '',
				'symbol': {
					'color': [255, 0, 0, 20],
					'outline': {'color': [230, 230, 0, 255], 'style': 'esriSLSSolid', 'type': 'esriSLS', 'width': 0.5625},
					'style': 'esriSFSSolid',
					'type': 'esriSFS'},
				'type': 'simple'
			}
		}
	}
	map_json_dict["baseMap"] = {
		"title": "Shared Imagery Basemap",
		"baseMapLayers": [{
				"url": "https://services.arcgisonline.com/ArcGIS/rest/services/ESRI_Imagery_World_2D/MapServer"
			}
			#{
			#	"id": "VectorTile_1933",
			#	"type": "VectorTileLayer",
			#	"layerType": "VectorTileLayer",
			#	"title": "World_Basemap",
			#	"styleUrl": "https://basemaps.arcgis.com/b2/arcgis/rest/services/World_Basemap/VectorTileServer/resources/styles/root.json",
			#	"visibility": True,
			#	"opacity": 1
			#}
			#{
			#	"id": "labels",
			#	"layerType": "ArcGISTiledMapServiceLayer",
			#	"url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer",
			#	"visibility": True,
			#	"opacity": 1,
			#	"title": "World_Dark_Gray_Base"
			#}#, {
			#	"id": "base",
			#	"layerType": "ArcGISTiledMapServiceLayer",
			#	"url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Reference/MapServer",
			#	"visibility": True,
			#	"opacity": 1,
			#	"title": "World_Dark_Gray_Reference"
			#}
	 		]}

	from pprint import pprint
	pprint(map_json_dict)

	map_json = json.dumps(map_json_dict)
	import arcpy

	# Convert the web map to an ArcGIS Project
	result = arcpy.mp.ConvertWebMapToArcGISProject(map_json)
	aprx = result.ArcGISProject

	# Get the map view
	m = aprx.listMaps()[0]
	mv = m.defaultView

	# Add feature set as a layer, symbolize

	map_image_path = 'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\map.png'

	# Export the web map
	mv.exportToPNG(map_image_path,result.outputSizeWidth, result.outputSizeHeight, result.DPI)

	# Set the output parameter to be the output file of the server job
	arcpy.SetParameterAsText(1, map_image_path)

	# Clean up
	del mv, m, aprx, result


	# Attempt to update Layer Definition
	#update_layer_def(item)

def grade_query_string():
    '''
    :return: SQL query string with correct syntax to check "Surface" and "Slope"
    fields. The result is all grade check observations with slopes that do not meet
    standards for their surface type. Works on Grade Check Observations AGOL Layer.
    '''
    return "(Surface = 'Asphalt' And (Slope > 10 Or Slope < 1.5)) Or (Surface = 'Heavy Duty Concrete' And (Slope > 10 Or Slope < 0.5)) Or (Surface = 'Curb and Gutter' And (Slope > 10 Or Slope < 0.5)) Or (Surface = 'Handicap Parking Area' And Slope > 2) Or (Surface = 'Sidewalk' And (Cross_Slope > 2 Or Running_Slope > 5))"

if __name__ == '__main__':
	main()
	#sys.exit(main())
