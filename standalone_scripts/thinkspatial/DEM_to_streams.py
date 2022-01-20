'''
May 9, 2019
Extract drainage lines from a digital elevation model
Warning: This process only has 5 steps, but it takes 
a long time, especially assigning stream orders
'''

import arcpy
from arcpy.sa import *

DEM = arcpy.GetParameterAsText(0)
workspace = arcpy.env.workspace
rivers = arcpy.GetParameterAsText(1)
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.extent = arcpy.GetParameterAsText(2)

arcpy.AddMessage("Filling sinks...")
fill = Fill(DEM)
arcpy.AddMessage("Generating flow direction...")
outFlowDirection = FlowDirection(fill) # you will use this 3 times
arcpy.AddMessage("Finding low points...")
flowAccumulation = FlowAccumulation(outFlowDirection)
arcpy.AddMessage("Recalculating...")
classified_FlowAcc = flowAccumulation > 3000
arcpy.AddMessage("Assigning stream orders...")
outStreamOrder = StreamOrder(classified_FlowAcc, outFlowDirection)
arcpy.AddMessage("Converting rivers to lines...")
StreamToFeature(outStreamOrder, outFlowDirection, rivers)
