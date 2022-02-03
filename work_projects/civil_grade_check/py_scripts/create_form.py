# import statements

# Data
from arcgis.gis import GIS                                      # Access AGOL
from arcgis.mapping import WebMap                               # Create map from webmap
from arcgis.apps.survey123 import SurveyManager, Survey         # Collect data from Survey123
from datetime import datetime as dt, timedelta as td            # Work with time and recent data filtering
import json                                                     # Work with AGOL data in json, python dictionary formats
import inspect                                                  # inspect.getmembers(*object*) is helpful for debugging
# Document
from io import BytesIO                                          # Allows Flask object to work with information in bytes
from docx.shared import Cm, Inches								# For images in word doc
from docxtpl import DocxTemplate, InlineImage					# For editing/updating template
from flask import Flask, send_file                              # Creates environment object to work with files
import docx2pdf													# Converts word document to pdf document
# Email
import smtplib                                                  # Environment to send emails
from pathlib import Path                                        # For identifying the attachment file name
from email.mime.multipart import MIMEMultipart                  # Create the message, subject, attachments, etc.
from email.mime.base import MIMEBase                            # Create attachment objects
from email.mime.text import MIMEText                            # Converts text message to deliverable object
from email.utils import COMMASPACE, formatdate                  # Email environment variables (To:, Sent-DateTime)
from email import encoders                                      # Email object translator/interpreter/compiler
# Map
import arcpy                                                    # Create map object, layers to export
from PIL import Image											# Convert map png image to pdf document
# Other
import civil_functions as cf                                    # Customized set of functions for civil projects
from pprint import pprint										# Great for testing, reading lists/dictionaries, etc.
print('libraries imported')

# access GIS and Survey123 #VERIFIED
gis = GIS('https://meiamerica.maps.arcgis.com/', 'chigham_mei', 'Kingchr23!')
sm = SurveyManager(gis)
print('connected to AGOL and Survey123')

# access field layer data, web map, survey #VERIFIED
grade_check_point_data = gis.content.get('89cd1d749f3c4e52ac8c78ebf853e909').layers[0]
web_map = WebMap(gis.content.get('fe73b29a5a5b4504adf43461366c74b6'))
base_map = web_map.basemap
grade_check_survey = sm.get('1e57b79836ed4f9880c053bbc249ebf1')
survey_results = gis.content.get('1115514027e1448eb88bcd26954ce700').layers[0]
print('AGOL items identified')

# filter map
web_map = cf.filter_layer_by_title(web_map, 'Grade check - create point')
print('filtered web map? do we need to do this?')

# query data (recent, does not fit grading standards)
query_result = cf.recent_grade_check_query(grade_check_point_data, 1024)
print('grade check point layer query returned')

# filter for the most recent survey
recent_surveys = cf.most_recent_surveys(survey_results, 1024)
last_survey = recent_surveys.features[len(recent_surveys.features) - 1].attributes
print('most recent survey identified')

# Get data from query_result, last_survey, and dt
client_name = last_survey['_to']                                # Survey123
client_company = last_survey['cc']                              # Survey123
meridian_engineer_name = last_survey['_from']                   # Survey123
today_s__date = dt.now().strftime('%B %d, %Y')					# Date Time
project_name = last_survey['project_name']                      # Survey123
project_number = last_survey['project_number']                  # Survey123
areas = last_survey['areas']                                    # Survey123
all_good = cf.response_to_grade_check_status(query_result)      # ArcGIS lyr
observations = cf.create_problem_table_list(query_result)       # ArcGIS lyr
row_contents = cf.return_row_contents(observations)             # ArcGIS lyr

# add data to a dictionary for word to extract
context = {
    'client_name': client_name,
    'client_company': client_company,
    'meridian_engineer_name': meridian_engineer_name,
    'today_s__date': today_s__date,
    'project_name': project_name,
    'project_number': project_number,
    'areas': areas,
    'all_good': all_good,
    'row_contents': row_contents,
    'image': ''
}
print('data extracted, ready to export deliverables')





# create a map image to insert into the word document

# Select a map to use as a starting point
def search_layer(conn, layer_name):
	search_results = conn.content.search(layer_name, item_type='*')
	proper_index = [i for i, s in enumerate(search_results) if '"' + layer_name + '"' in str(s)]
	found_item = search_results[0]#[proper_index[0]]
	get_item = conn.content.get(found_item.id)
	return get_item
#conn = GIS('https://meiamerica.maps.arcgis.com/', 'chigham_mei', 'Kingchr23!')  # Search for item, get item data)
item = search_layer(gis, 'Grade check observations')
map_json_dict = item.get_data()

# Add missing data to the dictionary
#map_json_dict["mapOptions"] = {"extent": {"xmin": -12550000, "ymin": 4850000, "xmax": -12350000, "ymax": 5000000, "spatialReference": {"wkid": 3857}}} # don't change this yet
map_json_dict["mapOptions"] = {"extent": {"xmin": -12456000, "ymin": 4941600, "xmax": -12455700, "ymax": 4941850, "spatialReference": {"wkid": 3857}}}  # until it's customized
#map_json_dict["exportOptions"] = {"dpi": 50, "outputSize": [1500, 900]}
map_json_dict["exportOptions"] = {"dpi": 150, "outputSize": [1800, 1100]}

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
		"definitionExpression": cf.grade_query_string(),
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
#map_json_dict["baseMap"] = {
#		"title": "Shared Imagery Basemap",
#		"baseMapLayers": [{
#				"url": "https://services.arcgisonline.com/ArcGIS/rest/services/ESRI_Imagery_World_2D/MapServer"
#				#"url": ""
#			}]
#}
map_json_dict["baseMap"] = json.loads(str(base_map))
print(map_json_dict["baseMap"])

# Convert dictionary back to json
map_json = json.dumps(map_json_dict)
# Convert the web map to an ArcGIS Project
result = arcpy.mp.ConvertWebMapToArcGISProject(map_json)
aprx = result.ArcGISProject
# Get the map view
m = aprx.listMaps()[0]
mv = m.defaultView
# Add reference layers
#lyr_list, l_list, pg_list = cf.hosted_feature_layer_to_fs_lists(gis, 'b3184fe167c445969c2154df6e24a359')
#b, lines_fc = cf.feature_set_lists_to_feature_classes(l_list, pg_list)
#reference_lines_lyr, reference_lines_lyrx, reference_lines_lyr_addable = cf.feature_classes_to_reference_layers(lines_fc, m)
cf.hosted_feature_layer_to_map(gis, 'b3184fe167c445969c2154df6e24a359', m)
#del p_fc, l_fc, pg_fc
#m.addLayer(p_l)
#m.addLayer(reference_lines_lyr_addable)
#m.addLayer(pg_l)
# Create Feature Class
arcpy.env.overwriteOutput = True
points_fc = arcpy.management.CreateFeatureclass('C:\\Temp', 'tempfc', 'POINT')[0]
# Add geometry from feature set
with arcpy.da.InsertCursor(points_fc, ['SHAPE@XY']) as cursor:
	for i in range(len(query_result.features)):
		x = query_result.features[i].geometry['x']
		y = query_result.features[i].geometry['y']
		cursor.insertRow([(x, y)])
# Create Layer with symbology from feature class
points_lyr = 'in_memory\\points_lyr.lyrx'
arcpy.MakeFeatureLayer_management(points_fc, 'points_lyr')
arcpy.SaveToLayerFile_management('points_lyr', points_lyr)
# Specify the sublayer to add to the map
points_lyrx = arcpy.mp.LayerFile(points_lyr)
points_lyr_addable = points_lyrx.listLayers()[0]

# Change symbology (do before adding to the map?)
symbology_lyr = arcpy.mp.LayerFile('U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\GIS\\symbology.lyrx')
symbology_sub_lyr = symbology_lyr.listLayers()[0]
arcpy.management.ApplySymbologyFromLayer(points_lyr_addable, symbology_sub_lyr)
print('symbology copied from template')
# Add Layer to map (move to after copying symbology?)
#print(inspect.getmembers(points_lyr_addable))
#print(inspect.getmembers(reference_lines_lyr_addable))
#m.addLayer(reference_lines_lyr_addable)
m.addLayer(points_lyr_addable, 'TOP')
print()
for thing in m.listLayers():
	print(thing)
print()
print('layer added to the map')
# Export the web map to png image
map_image_path = 'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\map.png'
mv.exportToPNG(map_image_path, result.outputSizeWidth, result.outputSizeHeight, result.DPI)
print('map exported as an image')
## Create a pdf of the map # perhaps not necessary
#map_image = Image.open(map_image_path)
#map_pdf = map_image.convert('RGB')
#map_pdf.save(map_image_path[:-3] + 'pdf')
#print('map saved as a pdf')
# Clean up
#del mv, m, aprx, result, points_fc, points_lyr, points_lyrx
#del p_fsl, l_fsl, pg_fsl#, p_fc, l_fc, pg_fc, p_l, l_l, pg_l
#del p_l, l_l, pg_l




# Populate variables in the word template, create word document
app = Flask(__name__)
template = 'grade_check.docx'
image = 'logo.png'
map_image = 'map.png'
output = 'output_test.docx'

@app.route('/')
def gen_docx(template, image, map_image, context, output):
	document = cf.from_template(template, image, map_image, context)
	document.seek(0)

	# save copy of the template, final output (word)
	with open(output, 'wb') as f:
		f.write(document.getbuffer())


with app.app_context():
	gen_docx(template, image, map_image, context, output)

print('word document created')

# convert word output to pdf
# needs work/function
output_pdf = output[:-4] + 'pdf'
docx2pdf.convert('U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\' + output, 'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\' + output_pdf)
print('docx converted to pdf')


# Email the final output to someone
# send an email with an attachment to self (engineer)
to_email = last_survey['email']
print('\nAn email: ' + to_email)

#if __name__ == '__main__':
#    main()
