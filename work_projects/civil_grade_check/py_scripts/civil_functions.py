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


def recent_grade_check_query(layer, number_of_hours=24):        # Works
    grade_query = grade_query_string()
    grade_time_query = f"(CreationDate > '{recent_time(number_of_hours)}') And ({grade_query})"
    queried = layer.query(where=grade_time_query)
    return queried

def filter_layer_by_title(webmap, layer_title):     # Works, but maybe not necessary
    for lyr in webmap.layers:
        if lyr['title'] == layer_title:
            lyr.visibility = False
            break
    return webmap

def most_recent_surveys(layer, number_of_hours=24):     # Works
    time_query = f"CreationDate > '{recent_time(number_of_hours)}'"
    recent_surveys = layer.query(where=time_query)
    return recent_surveys

def create_problem_table_list(feature_set):     # Works
    '''
    Returns a compound list of problem instances in ['id', 'surface', 'slope %']
    format. This compound list is iterated through to print observation information
    to the table on page 2 in the word document. The purpose of this function is to
    read the data from a feature set more easily by switching to a compound list.
    :param feature_set: A feature set data structure generated from the AGOL query
    command.
    :return: A compound python list of problem instances.
    '''
    observations = []
    i = 1

    for problem in feature_set:
        oid = str(i)
        surface = problem.attributes['Surface']
        slope = problem.attributes['Slope']
        cross = problem.attributes['Cross_Slope']
        running = problem.attributes['Running_Slope']

        if surface != 'Sidewalk':
            observations.append([oid, surface, str(slope) + '%'])
        elif surface == 'Sidewalk':
            observations.append([oid, f'{surface} (cross slope)', str(cross) + '%'])
            observations.append([oid, f'{surface} (running slope)', str(running) + '%'])

        i += 1

    return observations

def recent_time(number_of_hours=24):        # Works
    '''
    Generate a datetime object that represents a the earliest point in time that
    qualifies as recent. By default, that is 24 hours before execution time, but
    in create_form.py it may be further in the past for testing purposes.
    :param number_of_hours: How many hours (integer) constitutes recent? 24 is default.
    :return: Datetime object that defines the earliest limit of "recent".
    '''
    now = dt.now()
    recent = now - td(hours=number_of_hours)
    return recent

def grade_query_string():       # Works
    '''
    :return: SQL query string with correct syntax to check "Surface" and "Slope"
    fields. The result is all grade check observations with slopes that do not meet
    standards for their surface type. Works on Grade Check Observations AGOL Layer.
    '''
    return "(Surface = 'Asphalt' And (Slope > 10 Or Slope < 1.5)) Or (Surface = 'Heavy Duty Concrete' And (Slope > 10 Or Slope < 0.5)) Or (Surface = 'Curb and Gutter' And (Slope > 10 Or Slope < 0.5)) Or (Surface = 'Handicap Parking Area' And Slope > 2) Or (Surface = 'Sidewalk' And (Cross_Slope > 2 Or Running_Slope > 5))"

def response_to_grade_check_status(query_result):       # Works
    '''
    If the recent grade check was a success, meaning there were no problems, the word
    document should reflect the good news. Otherwise, the client should be warned
    that there are problem areas. This function generates the correct response to
    include in the output document based on the grade check results.
    :param query_result: An ArcGIS Online feature set object with results of grade
    check instances that did not meet standards.
    :return: A string response to include in your message to the client.
    '''

    # Possible messages
    all_good_response = 'It appeared as though all areas that had been placed fell within acceptable ranges for grading.'
    not_all_good_response = 'You failed. See the following page for details.'

    # Check query for bad grades, return appropriate message
    if len(query_result) == 0:
        return all_good_response
    elif len(query_result) > 0:
        return not_all_good_response
    else:
        return ''

def return_row_contents(observations):          # Works
    '''
    Returns a list of data specific to the grade check observations field schema.
    Data for each observation include the following fields: oid, surface, and slope.
    Each element of the list is a dictionary with these 3 fields as keys.
    Data from the output can be used to populate a table in Microsoft Word.
    :param observations: An ArcGIS Online feature set (can be a query result from
    the Layer.query() method).
    :return: A list of data for grade check observation points.
    '''

    # Create a new empty list
    row_contents = []

    # Copy data from Feature Set to list
    for ob in observations:
        row_contents.append({
            'oid': ob[0],
            'surface': ob[1],
            'slope': ob[2]
        })

    # Return new list
    return row_contents

### From Vanessa Ekwegh
def from_template(template, image, map_image, context):     # Works
    '''
    Creates a copy of a template with changes as an object.
    See here for context:
    https://blog.formpl.us/how-to-generate-word-documents-from-templates-using-python-cb039ea2c890
    Github repository:
    https://github.com/Vnessah/docx-gen
    Original file:
    https://github.com/Vnessah/docx-gen/blob/master/generate.py
    :param template: File name (or file name and file path) for the .docx template file.
    :param image: File name (or file name and file path) for a logo or other image to
    include in the document inline (MUST be PNG format).
    :param context: A dictionary with keys that match the keys in the word demplate document.
    The values in this dictionary will replace the text in the template.
    :return: An bytes object that can be saved as a .docx file.
    '''
    target_file = BytesIO()
    template = DocxTemplate(template)

    ## Modify these lines to include the map
    img_size = Cm(5)  # sets the size of the image
    sign = InlineImage(template, image, img_size)
    context['image'] = sign         # adds the InlineImage object (logo) to the context
    attachment = InlineImage(template, map_image, width=Inches(16))
    context['map'] = attachment     # adds the InlineImage object (map) to the context

    target_file = BytesIO()
    template.render(context)
    template.save(target_file)

    return target_file

def create_grade_check_map(web_map):        # Needs work
    original_map_json = create_json_from_map(web_map)

def create_json_from_map(webmap):       # Needs work

    web_map = WebMap(webmap)
    webmapJson = web_map.get_data()
    print(type(webmapJson))

    map_dict = {}

    map_dict['mapOptions'] = {}
    #map_dict['operationalLayers'] = web_map.operationalLayers
    #print(web_map.__dict__)
    map_dict['baseMap'] = web_map.basemap       # Works
    #print(map_dict['baseMap'])
    map_dict['exportOptions'] = {}
    map_dict['layoutOptions'] = {}

    map_json = json.dump(map_dict, 'output.json')
    return map_json

def create_map(query_result):       # Needs testing
    from arcgis.gis import GIS
    conn = GIS('https://meiamerica.maps.arcgis.com/', 'chigham_mei', 'Kingchr23!')  # Search for item, get item data)
    item = search_layer(conn, 'Grade check observations')
    map_json_dict = item.get_data()

    # Add missing data to the dictionary
    map_json_dict["mapOptions"] = {"extent": {"xmin": -12550000, "ymin": 4850000, "xmax": -12350000, "ymax": 5000000, "spatialReference": {"wkid": 3857}}}
    map_json_dict["exportOptions"] = {"dpi": 50, "outputSize": [1500, 900]}
    #from copy import copy
    # #map_json_dict["operationalLayers"] = [{"layers": copy(map_json_dict["layers"])}]
    # #del map_json_dict["layers"]
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
    import arcpy
    #Create feature class
    points_fc = arcpy.CreateFeatureclass_management('in_memory', 'tempfc', 'POINT')[0]
    coordinates_fc = []
    for i in range(len(query_result.features)):
        x = query_result.features[i].geometry['x']
        y = query_result.features[i].geometry['y']
        coordinates_fc.append([x, y])
    with arcpy.da.InsertCursor(points_fc, ['SHAPE@XY']) as cursor:
        for (x, y) in coordinates_fc:
            cursor.insertRow([(x, y)])
    #Create Layer with symbology
    points_lyr = arcpy.MakeFeatureLayer_management(points_fc, 'points_lyr')
    sym_dict = json.loads(points_lyr._arc_object.getsymbology())
    print(sym_dict)
    #Insert Layer

    map_image_path = 'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\map.png'

    # Export the web map
    mv.exportToPNG(map_image_path,result.outputSizeWidth, result.outputSizeHeight, result.DPI)

    # Set the output parameter to be the output file of the server job
    arcpy.SetParameterAsText(1, map_image_path)

    # Clean up
    del mv, m, aprx, result, points_fc, points_lyr       # Needs testing

'''import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders'''

def send_mail(send_from, send_to, subject, text, files=[], server='localhost',  # Needs testing
              port=587, username='', password='', use_tls=True):
    '''Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name ('localhost' or 'smtp.gmail.com' are options)
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    '''

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for path in files:
        part = MIMEBase('application', 'octet-stream')
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename={Path(path).name}')
        msg.attach(part)

    smtp = smtplib.SMTP(server, port) # Maybe change server to 'smtp.gmail.com'? See water rights example

    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

def hosted_feature_layer_to_fs_lists(gis, hosted_feature_layer):            # Needs work
    reference_AGOL = gis.content.get(hosted_feature_layer)#'b3184fe167c445969c2154df6e24a359'
    lyr_list = reference_AGOL.layers
    #p_list = []
    l_list = []
    pg_list = []
    for lyr in lyr_list:
        lyr_fs = lyr.query(where='OBJECTID > -1')

        # Add to one of the 3 geometry type lists
        if lyr_fs.geometry_type == 'esriGeometryPoint':
            pass
        #    for feat in lyr_fs.features:
        #        p_list.append(feat.geometry)
        elif lyr_fs.geometry_type == 'esriGeometryPolyline':
            for feat in lyr_fs.features:
                l_list.append(feat.geometry)
        elif lyr_fs.geometry_type == 'esriGeometryPolygon':
            for feat in lyr_fs.features:
                pg_list.append(feat.geometry)
    #return p_list, l_list, pg_list
    return lyr_list, l_list, pg_list  # l_list is the variable of choice

#def feature_set_lists_to_feature_classes(p_list, l_list, pg_list):
def feature_set_lists_to_feature_classes(l_list, pg_list):
    from copy import deepcopy
    arcpy.env.overwriteOutput = True
    ## points
    #a = deepcopy(p_list)
    #points_sr = a[0]['spatialReference']['latestWkid']
    #points_fc = arcpy.management.CreateFeatureclass('C:\\Temp', 'temp_fc_p', 'POINT', spatial_reference=points_sr)[0]
    #with arcpy.da.InsertCursor(points_fc, ['SHAPE@XY']) as cursor:
    #    for point in a:
    #        cursor.insertRow([(point['x'], point['y'])])
    # lines
    b = deepcopy(l_list)
    lines_sr = b[0]['spatialReference']['latestWkid']
    lines_fc = arcpy.management.CreateFeatureclass('C:\\Temp', 'temp_fc_l', 'POLYLINE', spatial_reference=lines_sr)[0]
    with arcpy.da.InsertCursor(lines_fc, ['SHAPE@']) as cursor:
        for line in b:
            for path in line['paths']:
                cursor.insertRow([path])
        for polygon in pg_list:
            for ring in polygon['rings']:
                cursor.insertRow([ring])
    ## polygons
    #c = deepcopy(pg_list)
    #polygon_sr = c[0]['spatialReference']['latestWkid']
    #polygon_fc = arcpy.management.CreateFeatureclass('C:\\Temp', 'temp_fc_pg', 'POLYGON', spatial_reference=polygon_sr)[0]
    #with arcpy.da.InsertCursor(polygon_fc, ['SHAPE@']) as cursor:
    #    for polygon in c:
    #        for ring in polygon['rings']:
    #            cursor.insertRow([ring])

    #return points_fc, lines_fc, polygon_fc
    return b, lines_fc

#def feature_classes_to_reference_layers(points_fc, lines_fc, polygon_fc):
def feature_classes_to_reference_layers(lines_fc, m):
    #from copy import deepcopy
    from pprint import pprint
    ## points
    #a = deepcopy(points_fc)
    #reference_points_lyr = 'in_memory\\reference_points_lyr.lyrx'
    #arcpy.MakeFeatureLayer_management(a, 'reference_points_lyr')
    #arcpy.SaveToLayerFile_management('reference_points_lyr', reference_points_lyr)
    #reference_points_lyrx = arcpy.mp.LayerFile(reference_points_lyr)
    #reference_points_lyr_addable = reference_points_lyrx.listLayers()[0]

    # lines
    #c = deepcopy(lines_fc)
    reference_lines_lyr = 'in_memory\\reference_lines_lyr.lyrx'
    arcpy.MakeFeatureLayer_management(lines_fc, 'reference_lines_lyr')
    arcpy.SaveToLayerFile_management('reference_lines_lyr', reference_lines_lyr)
    reference_lines_lyrx = arcpy.mp.LayerFile(reference_lines_lyr)
    reference_lines_lyr_addable = reference_lines_lyrx.listLayers()[0]
    print(type(reference_lines_lyrx))
    print(type(reference_lines_lyr_addable))
    symbology_line_lyr = arcpy.mp.LayerFile(
        'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\GIS\\reference_lines.lyrx').listLayers()[0]
    arcpy.management.ApplySymbologyFromLayer(reference_lines_lyr_addable, symbology_line_lyr)
    #reference_lines_lyr_addable = arcpy.management.ApplySymbologyFromLayer(reference_lines_lyr_addable, symbology_line_lyr)
    m.addLayer(symbology_line_lyr)


    #symbology_lyr = arcpy.mp.LayerFile(
    #    'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\GIS\\symbology.lyrx')
    #symbology_sub_lyr = symbology_lyr.listLayers()[0]
    #arcpy.management.ApplySymbologyFromLayer(points_lyr_addable, symbology_sub_lyr)

    ## polygons
    #c = deepcopy(polygon_fc)
    #reference_polygons_lyr = 'in_memory\\reference_polygons_lyr.lyrx'
    #arcpy.MakeFeatureLayer_management(c, 'reference_polygons_lyr')
    #arcpy.SaveToLayerFile_management('reference_polygons_lyr', reference_polygons_lyr)
    #reference_polygons_lyrx = arcpy.mp.LayerFile(reference_polygons_lyr)
    #reference_polygons_lyr_addable = reference_polygons_lyrx.listLayers()[0]

    # return 3 layers
    #return reference_points_lyr_addable, reference_lines_lyr_addable, reference_polygons_lyr_addable
    #return reference_lines_lyr, reference_lines_lyr_addable
    #return c, reference_lines_lyr, reference_lines_lyrx, reference_lines_lyr_addable
    return reference_lines_lyr, reference_lines_lyrx, reference_lines_lyr_addable

def hosted_feature_layer_to_map(gis, hosted_feature_layer, m):

    # hosted layer to list
    reference_AGOL = gis.content.get(hosted_feature_layer)  # 'b3184fe167c445969c2154df6e24a359'
    lyr_list = reference_AGOL.layers
    # p_list = []
    l_list = []
    pg_list = []
    for lyr in lyr_list:
        lyr_fs = lyr.query(where='OBJECTID > -1')

        # Add to one of the 3 geometry type lists
        if lyr_fs.geometry_type == 'esriGeometryPoint':
            pass
        #    for feat in lyr_fs.features:
        #        p_list.append(feat.geometry)
        elif lyr_fs.geometry_type == 'esriGeometryPolyline':
            for feat in lyr_fs.features:
                l_list.append(feat.geometry)
        elif lyr_fs.geometry_type == 'esriGeometryPolygon':
            for feat in lyr_fs.features:
                pg_list.append(feat.geometry)

    # List to feature class
    from copy import deepcopy
    arcpy.env.overwriteOutput = True
    b = deepcopy(l_list)
    lines_sr = b[0]['spatialReference']['latestWkid']
    lines_fc = arcpy.management.CreateFeatureclass('C:\\Temp', 'reference_lyr', 'POLYLINE', spatial_reference=lines_sr)[0]
    with arcpy.da.InsertCursor(lines_fc, ['SHAPE@']) as cursor:
        for line in b:
            for path in line['paths']:
                cursor.insertRow([path])
        for polygon in pg_list:
            for ring in polygon['rings']:
                cursor.insertRow([ring])

    # Feature class to layer
    reference_lyr = 'U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\py_scripts\\in_memory\\reference_lyr.lyrx'
    arcpy.MakeFeatureLayer_management(lines_fc, 'reference_lyr')
    #ref_layer = arcpy.MakeFeatureLayer_management(lines_fc, 'reference_lyr')[0]
    arcpy.SaveToLayerFile_management('reference_lyr', reference_lyr)
    reference_lyrx = arcpy.mp.LayerFile(reference_lyr)
    reference_lyr_addable = reference_lyrx.listLayers()[0]
    symbology_line_lyr = arcpy.mp.LayerFile('U:\\Departments\\LiDAR-GIS\\GIS Backup\\Other Requests\\2020\\2020-12-10 - Civil pdf project\\GIS\\reference_lines.lyrx')
    symbology_line_sub_layer = symbology_line_lyr.listLayers()[0]
    arcpy.management.ApplySymbologyFromLayer(reference_lyr_addable, symbology_line_sub_layer)

    # Layer to map
    m.addLayer(reference_lyr_addable)
    #m.addLayer(ref_layer)
