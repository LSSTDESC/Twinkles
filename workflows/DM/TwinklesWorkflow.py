from java.util import HashMap

def setupFilters():
   filters = ['u','g','r','i','z','y']	
   vars = HashMap()
   i = 0
   for filter in filters:
     vars.put("FILTER",filter)
     visits = []
     f = open(SLAC_SCRIPT_LOCATION+"/"+VISIT_FILE)
     for line in f.readlines():
        dir,visit,f = line.split()
        if filter==f:
           visits.append(visit)  
     vars.put("VISITS","^".join(visits))
     print i,vars
     pipeline.createSubstream("processFilter",i,vars)
     i += 1

def setupVisits():
   vars = HashMap()
   for visit in VISITS.split("^"):
      vars.put("VISIT",visit)
      pipeline.createSubstream("processVisit",int(visit),vars)

def setupEimageVisits():
   vars = HashMap()
   f = open(SLAC_SCRIPT_LOCATION+"/"+VISIT_FILE)
   for line in f.readlines():
      dir,visit,f = line.split()
      vars.put("FILTER",f)
      vars.put("VISIT",visit)
      pipeline.createSubstream("processVisit",int(visit),vars)

def setupForcedPhotometryVisits():
   vars = HashMap()
   f = open(SLAC_SCRIPT_LOCATION+"/"+VISIT_FILE)
   for line in f.readlines():
      dir,visit,f = line.split()
      vars.put("FILTER",f)
      vars.put("VISIT",visit)
      pipeline.createSubstream("processForcedPhotometry",int(visit),vars)
