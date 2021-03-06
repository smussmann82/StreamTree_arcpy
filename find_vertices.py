from __future__ import print_function
import arcpy
import os
from comline import ComLine

class FindVertices():
	'Class for finding vertices corresponding to sampling sites and stream intersections in an ESRI shapefile containing lines representing interconnected streams'
	def __init__(self,points,streams,code):
		# set workspace
		arcpy.env.workspace = os.getcwd()
		arcpy.env.overwriteOutput=True
		arcpy.env.XYResolution = "1 Meters"
		arcpy.env.XYTolerance = "1 Meters"
		
		dissolved = self.dissolve_lines(streams, "streams_dissolve.shp") #dissolve a streams layer with many line segments
		self.snap_points(points, dissolved)#snap points to the streams to ensure they will accurately split the lines
		self.splits = self.split_line(points,dissolved,"split_streams.shp") #split all lines at the sampling sites
		endpoints = self.end_points(self.splits,"end_points.shp") #make endpoints for resulting split streams from previous command
		self.add_xy(endpoints) #add XY cooridnates to attribute table of the endpoints that were created for all lines
		self.add_xy(points) #add XY coordinates to attribute table of sampling sites
		self.remove_identical(endpoints) #remove redundant points at ends of stream segments
		erased = self.erase_points(endpoints,points,"end_points_dissolve_erase.shp")
		self.vertices = self.merge_points(erased,points,"all_vertices.shp",code)

	def dissolve_lines(self,streams,out):
		print("Dissolving input streams file", streams)
		print("")
		arcpy.Dissolve_management(streams, out, "", "", "SINGLE_PART")
		return out

	def snap_points(self,points, dissolved):
		print("Snapping points file", points, "to", dissolved)
		print("")
		arcpy.Snap_edit(points, [[dissolved, "VERTEX", "2 Kilometers"]])

	def split_line(self,points, dissolved,out):
		print("Splitting", dissolved, "at", points, "and writing to", out)
		print("")
		arcpy.SplitLineAtPoint_management(dissolved,points,out,"1 Meters")
		return out

	def end_points(self,splits,out):
		print("Making end points")
		print("")
		arcpy.FeatureVerticesToPoints_management(splits,out,"BOTH_ENDS")
		return out
	
	def add_xy(self,input):
		print("Adding XY coordinates to", input)
		print("")
		arcpy.AddXY_management(input)
	
	def remove_identical(self,endpoints):
		print("Removing redundant endpoints from", endpoints)
		print("")
		arcpy.DeleteIdentical_management(endpoints,["POINT_X","POINT_Y"],"1 Meters")
	
	def erase_points(self,endpoints,points,out):
		print("Removing points in", endpoints, "that are redundant with sampling locations")
		print("")
		arcpy.Erase_analysis(endpoints,points,out,"1 Meters")
		return out
	
	def merge_points(self,erased,points,out,code):
		print("Merging into final output")
		print("")
		fieldMappings = arcpy.FieldMappings()#create fieldmapping object
		fieldMappings.addTable(erased)#get fields from erased
		fieldMappings.addTable(points)#get fields from points
		for field in fieldMappings.fields:
			if field.name not in ["POINT_X","POINT_Y",code]:
				fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
		arcpy.Merge_management([erased,points],out,fieldMappings)
		return out