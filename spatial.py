
#import & transform the required data
import arcpy
from arcpy import env
from arcpy.sa import *


uni_dir = "H:\\Spatial_Analysis\\assessment\\"
home_dir = "C:\\Users\\Alec\\Documents\\Spatial_Analysis\\Data\\" # reduces redundancy and simplifies working on code across multiple machines. Double backslashes are to prevent python reading \ as an escape character
#test_dir = instert new string

 
#set as appropriate, from here on it it should work without editing

directory = uni_dir

arcpy.CreateFileGDB_management(directory, "project.gdb")
arcpy.env.workspace = (directory + "project.gdb")
arcpy.MakeFeatureLayer_management(directory+"bounds.shp", 'geopol')
#convert all the required asciis to rasters and save in project file, dictionary to improve readability:
presentasciis =  {"amii.asc":"ami",
                 "absmintempi.asc":"absmintemp",
                 "annpreci.asc": "annpreci",
                 "mtempcoldi.asc": "mtempcold",
                 "mtempwarmi.asc": "mtempwarm"}

def batch_asc(asciis):
    for asc in asciis:
        arcpy.ASCIIToRaster_conversion(directory + asc, directory+"project.gdb\\" + asciis[asc], "FLOAT")

batch_asc(presentasciis)

arcpy.MakeXYEventLayer_management(directory+"species.csv","long","lat","speciespoint") # add species point data
arcpy.PointToRaster_conversion("speciespoint","sp4821", directory+"project.gdb\\presrast","MAXIMUM", "", "1") # set values to presence absence of my species and match resolution to environmental data

variables = presentasciis.values()

Sample(variables, "presrast", directory + "project.gdb\\sample", "NEAREST") # less redundancy than a series of map algebra calculations

# i was surprised there wasn't a tool to do this directly in the library, but this method worked fine. No numpy in case this caused protability issues
def get_minmax(value): 
	items = []
	rows = arcpy.SearchCursor("sample", "presrast = 1") #select only the rows where presence = 1
	for row in rows:
		item = row.getValue(value)
		items.append(item) # make a list for all the values of the variable being examined 
	minimum = (sorted(items))[0] # get lowest value
	maximum	= (sorted(items))[-1] # and highest
	return {"maximum": maximum, "minimum": minimum}

	
envelope = {}
for variable in variables:
	envelope[variable] = get_minmax(variable)


def get_theo(outname, invariables):
    query = []
    for variable in invariables:
    	if any(char.isdigit() for char in variable): #distinguish future variables from present ones
    		envariable = variable[:-2] #knock off the year to get the envelope key
        	clause = "((Raster('%s') >= %s) & (Raster('%s') <= %s))" % (variable, envelope[envariable]['minimum'], variable,envelope[envariable]['maximum']) # creates a clause for each future variable
    	else:
        	clause = "((Raster('%s') >= %s) & (Raster('%s') <= %s))" % (variable, envelope[variable]['minimum'], variable,envelope[variable]['maximum']) # creates a clause for each present variable
        query.append(clause) # adds each clause in turn to the list
    query = " & ".join(query) #list to string with delimiter
    query = ("%s = " % outname) + query #make the outname definable from the call
    #print query
    return(query) # pass the query back - for some reason if it's run from within a function it doesn't work, which is
                  # also the reason for all the redundancy below

query = get_theo("EnvelopeNow", variables)
exec(query)# run the query as python code
EnvelopeNow.save(directory + "project.gdb\\EnvelopeNow") # add to geodatabase

asciis_25 = {"amii2025.asc":"ami25",
             "absmintempi2025.asc":"absmintemp25",
             "annpreci2025.asc": "annpreci25",
             "mtempcoldi2025.asc": "mtempcold25",
             "mtempwarmi2025.asc": "mtempwarm25"}
batch_asc(asciis_25)
variables25 = asciis_25.values() 
query25 = get_theo("Envelope25", variables25)
exec(query25)
Envelope25.save(directory + "project.gdb\\Envelope25")

Envelopenowclip = Con(Raster('presrast') >= 0, Raster('EnvelopeNow')) 
    

asciis_55 = {"amii2055.asc":"ami55",
             "absmintempi2055.asc":"absmintemp55",
             "annpreci2055.asc": "annpreci55",
             "mtempcoldi2055.asc": "mtempcold55",
             "mtempwarmi2055.asc": "mtempwarm55"}
batch_asc(asciis_55)
variables55 = asciis_55.values() 
query55 = get_theo("Envelope55", variables55)
exec(query55)
Envelope55.save(directory + "project.gdb\\Envelope55")


asciis_85 = {"amii2085.asc":"ami85",
             "absmintempi2085.asc":"absmintemp85",
             "annpreci2085.asc": "annpreci85",
             "mtempcoldi2085.asc": "mtempcold85",
             "mtempwarmi2085.asc": "mtempwarm85"}
batch_asc(asciis_85)
variables85 = asciis_85.values() # put the values in a new variable list
query85 = get_theo("Envelope85", variables85)
exec(query85)
Envelope85.save(directory + "project.gdb\\Envelope85")

Pers25 = ((Raster('presrast') == 1) & (Raster('Envelope25') == 1))
Pers55 = ((Raster('presrast') == 1) & (Raster('Envelope55') == 1))
Pers85 = ((Raster('presrast') == 1) & (Raster('Envelope85') == 1))


ZAtabpres = ZonalStatisticsAsTable("Envelopenowclip", "Value", "africa_dem",
                                  "zonalnow", "DATA", "MEAN")
ZAtabpres2 = ZonalStatisticsAsTable("Envelope25", "Value", "africa_dem",
                                  "zonal25", "DATA", "MEAN")
ZAtabpres3 = ZonalStatisticsAsTable("Envelope55", "Value", "africa_dem",
                                  "zonal55", "DATA", "MEAN")
ZAtabpres4 = ZonalStatisticsAsTable("Envelope85", "Value", "africa_dem",
                                  "zonal85", "DATA", "MEAN")

