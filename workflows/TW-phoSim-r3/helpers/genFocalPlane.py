#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

"""
genFocalPlane.py - create a text file containing all sets of phoSim
sensor locations for use as command line options, e.g.,"-s
R122_S11" is the sensor in the very center of the focal plane.

Strings are of the format Rxy_Sxy, where Rxy = raft location on focal
plane (x and y = 0-4), and Sxy = sensor location within raft (x and y = 0-2).
Note that R00, R04, R40 and R44 are special 'corner rafts', each with only three sensors.

"""
raftDim = [0,1,2,3,4]
sensorDim = [0,1,2]
corners = ['00','04','40','44']
sensorTot = 0

fd = open('sensorList.txt','w')

for rx in raftDim:
    for ry in raftDim:
        rxy = str(rx)+str(ry)
        if rxy in corners: continue  ## No corner rafts
#        if rxy != '22': continue     ## Center raft only
        for sx in sensorDim:
            for sy in sensorDim:
                sxy = str(sx)+str(sy)
                sensorTot += 1
                sensor = 'R'+rxy+'_'+'S'+sxy
                print sensor
                fd.write(sensor+'\n')
                pass
            pass
        pass
    pass

fd.close()
print 'sensorTot = ',sensorTot


