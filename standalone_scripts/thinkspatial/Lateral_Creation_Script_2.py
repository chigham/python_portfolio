'''
Script originally written by Kasey Hansen at Gateway mapping
Modified by Christopher Higham for a specific project January 2020
'''
#Kasey Hansen
#November 18th, 2015 (Happy Thanksgiving!)
#Lateral Creation Tool (For Real)

#This script will allow you to take point layer showing sewer lateral locations along a mainline pipe, and turn them into stubs along the pipe.
#Stubs will be perpendicular to the main pipe, and will extend out a distance specified by the user.

import arcpy,math,os

#------------------Function 'GetLateralEndCoords' to calculate the end points--------------------------------------------------
#Inputs required from each lateral point:
    ##X and Y coordinates of the start point of the mainline pipe (In this script, we'll get this using the mainline Pipe ID already assigned to the lateral point) - inputs "X0" and "Y0"
    ##X and Y coordinates of lateral point  - inputs "X1" and "Y1"
    ##Length of lateral - Variable "L" - input "L"
    ##Side of lateral  (Left/Right) - input "Side"
#Function returns a tuple with X and Y coordinates of lateral end point

def GetLateralEndCoords(X0,Y0,X1,Y1,L,Side):
    #First, calculate the variables that are consistent no matter which quadrant/side the pipe lands in
    X2 = abs(X1-X0)
    Y2 = abs(Y1-Y0)
    D = math.sqrt((X2**2)+(Y2**2))
    D2 = math.sqrt((L**2)+(D**2))
    A1 = math.degrees(math.atan((L/D)))

    #If the mainline pipe bearing is in Quadrant 1...
    if (X1 > X0) and (Y1 > Y0):
        arcpy.AddMessage("Quadrant 1")
        if Side == "Left":
            A2 = math.degrees(math.atan((Y2/X2)))
            X = D2*math.cos(math.radians(A1+A2))
            Y = D2*math.sin(math.radians(A1+A2))
            FinalX = X0 + X
            FinalY = Y0 + Y
        if Side == "Right":
            A2 = math.degrees(math.atan((Y2/X2)))- A1
            X = D2*math.cos(math.radians(A2))
            Y = D2*math.sin(math.radians(A2))
            FinalX = X0 + X
            FinalY = Y0 + Y

    #If the mainline pipe bearing is in Quadrant 2...
    elif (X1 < X0) and (Y1 > Y0):
        arcpy.AddMessage("Quadrant 2")
        if Side == "Left":
            A2 = math.degrees(math.atan((X2/Y2)))
            X = D2*math.sin(math.radians(A1+A2))
            Y = D2*math.cos(math.radians(A1+A2))
            FinalX = X0 - X
            FinalY = Y0 + Y
        if Side == "Right":
            A2 = math.degrees(math.atan((X2/Y2))) - A1
            X = D2*math.sin(math.radians(A2))
            Y = D2*math.cos(math.radians(A2))
            FinalX = X0 - X
            FinalY = Y0 + Y

    #If the mainline pipe bearing is in Quadrant 3...
    elif (X1 < X0) and (Y1 < Y0):
        arcpy.AddMessage("Quadrant 3")
        if Side == "Left":
            A2 = math.degrees(math.atan((Y2/X2)))
            X = D2*math.cos(math.radians(A1+A2))
            Y = D2*math.sin(math.radians(A1+A2))
            FinalX = X0 - X
            FinalY = Y0 - Y
        if Side == "Right":
            A2 = math.degrees(math.atan((Y2/X2)))- A1
            X = D2*math.cos(math.radians(A2))
            Y = D2*math.sin(math.radians(A2))
            FinalX = X0 - X
            FinalY = Y0 - Y
    elif (X1 > X0) and (Y1 < Y0):
        arcpy.AddMessage("Quadrant 4")
        if Side == "Left":
            A2 = math.degrees(math.atan((X2/Y2)))
            X = D2*math.sin(math.radians(A1+A2))
            Y = D2*math.cos(math.radians(A1+A2))
            FinalX = X0 + X
            FinalY = Y0 - Y
        if Side == "Right":
            A2 = math.degrees(math.atan((X2/Y2))) - A1
            X = D2*math.sin(math.radians(A2))
            Y = D2*math.cos(math.radians(A2))
            FinalX = X0 + X
            FinalY = Y0 - Y
    else:
        arcpy.AddMessage("No Quadrant!!!")
        if X0 == X1:
            if Y0 > Y1:
                if Side == "Right":
                    FinalY = Y1
                    FinalX = X1 - L
                elif Side == "Left":
                    FinalY = Y1
                    FinalX = X1 + L
            elif Y0 < Y1:
                if Side == "Right":
                    FinalY = Y1
                    FinalX = X1 + L
                elif Side == "Left":
                    FinalY = Y1
                    FinalX = X1 - L
        elif Y0 == Y1:
            if X0 > X1:
                if Side == "Right":
                    FinalY = Y1 + L
                    FinalX = X1
                elif Side == "Left":
                    FinalY = Y1 - L
                    FinalX = X1
            elif X0 < X1:
                if Side == "Right":
                    FinalY = Y1 - L
                    FinalX = X1
                elif Side == "Left":
                    FinalY = Y1 + L
                    FinalX = X1
        else:
            FinalX = 0
            FinalY = 0
    #print X2,Y2,D,D2,A1,A2,X
    arcpy.AddMessage(FinalX)
    arcpy.AddMessage(FinalY)
    return FinalX,FinalY

#---------------------------------Main Script-------------------------------------------------

#General Inputs - Make these match your data!!!!
LateralPointFC = r"\\oremfiles\Public\Mappers\PROJECTS\GMI\Kootenai\20-05-076 Kootenai Ponderay Sewer Dist\_136_2016 Mapbook Update\GIS\Finished_Backup.gdb\Laterals_Points_3_Temp"    #Full path to Lateral Point Feature Class
MainLineFC = r"\\oremfiles\Public\Mappers\PROJECTS\GMI\Kootenai\20-05-076 Kootenai Ponderay Sewer Dist\_136_2016 Mapbook Update\GIS\Finished_Backup.gdb\Joined_Sewer_Lines"     #Full path to Main Line Feature Class
LateralLineFC = r"\\oremfiles\Public\Mappers\PROJECTS\GMI\Kootenai\20-05-076 Kootenai Ponderay Sewer Dist\_136_2016 Mapbook Update\GIS\Finished_Backup.gdb\Laterals_Points_3_Temp_Lines"                   #Full path to Lateral Line Feature Class - the one that will be generated and have the lateral lines drawn onto it
LatPointIDField = "LineID"                 #Name of field on the Lateral Point Layer that holds the ID that matches the Mainline Layer
MainLineIDField = "LineID"                 #Name of field on the Main Line layer that holds the Main Line's ID - which should match up with a value in LatPointIDfield
LatPointSideField = "Side"          #Name of field on the Lateral Point Layer that says which side the lateral is on
LateralLength = 30                          #Lateral Length
#UpstreamDownstreamField = "FlowDirect"   #Name of field that says whether the lateral was measured going upstream or downstream

#First, Generate the lateral line feature class, and give it the same fields as the lateral point feature class
if arcpy.Exists(LateralLineFC):
    arcpy.Delete_management(LateralLineFC)
    arcpy.AddMessage("Deleting Old Lateral Line Layer.....")
arcpy.CreateFeatureclass_management(os.path.dirname(LateralLineFC),os.path.basename(LateralLineFC),"POLYLINE",LateralPointFC)
arcpy.AddMessage("Generating New Lateral Line Layer.....")

#Next, cycle through each point in the lateral points layer.  Get its X&Y coords and side.  Then, cycle through the main pipes layer to find the pipe the lateral is attached to, and get its starting X and Y coords.
PointCursor = arcpy.SearchCursor(LateralPointFC)
ICursor = arcpy.InsertCursor(LateralLineFC)
pcRow = PointCursor.next()
while pcRow:
    currentID = pcRow.getValue(LatPointIDField)
    currentSide = pcRow.getValue(LatPointSideField)
#Account for upstream runs going backwards from downstream runs. Do this by flipping the side on which the lateral plots
#    if pcRow.getValue(UpstreamDownstreamField) == "Upstream":
#        if currentSide == "Left":
#            currentSide = "Right"
#        else:
#            currentSide = "Left"
#    if currentSide == "Top":
#        currentSide = "Left"  #'Top' doesn't work for drawing, so we'll just draw any 'Top's on the left side of the pipe.  The attributes will ultimately still say "top"; this just changes where it draws.
#
    LatPointX = pcRow.SHAPE.firstPoint.X
    LatPointY = pcRow.SHAPE.firstPoint.Y
    MainCursor = arcpy.SearchCursor(MainLineFC)
    mnRow = MainCursor.next()
    while mnRow:
        if mnRow.getValue(MainLineIDField) == currentID:
            MainPointX = mnRow.SHAPE.firstPoint.X
            MainPointY = mnRow.SHAPE.firstPoint.Y
            #break
        mnRow = MainCursor.next()
    LatEndCoords = GetLateralEndCoords(MainPointX,MainPointY,LatPointX,LatPointY,LateralLength,currentSide) # <--Feed all of the information gathered into the function to return the end X and Y coords of the lateral
    arcpy.AddMessage(currentID)
#	 currentSide LatPointX LatPointY LatEndCoords

#Now that we have all the info we need, draw and add the lateral line to the lateral line layer (we're still in the while loop that cycles through the lateral points layer)
    LatStartPoint = pcRow.SHAPE.firstPoint
    LatEndPoint = arcpy.Point()
    LatEndPoint.X = LatEndCoords[0]
    LatEndPoint.Y = LatEndCoords[1]
    MyArray = arcpy.Array()
    MyArray.add(LatStartPoint)
    MyArray.add(LatEndPoint)
    MyPolyLine = arcpy.Polyline(MyArray)
    arcpy.AddMessage("Drawing lateral.....")
    irow = ICursor.newRow()
    irow.SHAPE = MyPolyLine

#Now cycle through the fields in the lateral point layer, and add the corresponding data to the laterals layer.  This works because the schemas are identical.
    fieldlist = arcpy.ListFields(LateralPointFC)
    for fld in fieldlist:
        if fld.type != "OID" and fld.type != "Geometry":
            try:
                irow.setValue(fld.name,pcRow.getValue(fld.name))
            except:
                arcpy.AddMessage("Field " + fld.name + " could not be populated.....")

    ICursor.insertRow(irow)
    #arcpy.Append_management(MyPolyLine,LateralLineFC,"NO_TEST")
    pcRow = PointCursor.next()

del PointCursor
del ICursor
del MainCursor

arcpy.AddMessage("Done!!!")






