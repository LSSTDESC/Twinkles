"""
Each instance catalog has a list of spectra that are also written to disk,
and these instance catalogs are written in mutliple runs. 
This module tries to check that all the files 

"""
from __future__ import absolute_import
import pandas as pd
import os


class ValidatePhoSimCatalogs(object):
    MegaByte = 1024*1024

    def __init__(self,
                 obsHistIDValues,
                 prefix='InstanceCatalogs/phosim_input_'):
        self.obsHistIDValues = obsHistIDValues
        self.prefix = prefix

    @classmethod
    def fromRunlog(cls, runlog='run.log',
                   prefix='InstanceCatalogs/phosim_input_',
                   obsHistIDrange=[0, None]):
        runs = pd.read_csv(runlog)

        if obsHistIDrange[-1] is None:
            obsHistIDrange[-1] = len(runs)
        
        obsHistIDValues = runs.obsHistID.values[obsHistIDrange[0]:obsHistIDrange[1]]
        return cls(obsHistIDValues=obsHistIDValues, prefix=prefix)

    @staticmethod
    def filenames(obsHistID, prefix='InstanceCatalogs/phosim_input_'):
        """
        return the filenames for the phosim instance catalog and the
        spectra tar ball corresponding to the obsHistID.
        """
        basename = prefix + str(obsHistID) 
        spectra_tar = basename + '.tar.gz'
        phosimInstanceCatalog = basename + '.txt.gz'
        return phosimInstanceCatalog, spectra_tar

    @staticmethod
    def validateSizes(phosimInstanceCatalog, spectra_tar, unitSize,
                      minSizePhosim=15, minSizeSpectra=40):
        """
        Check that the files exist and have sizes above a minimum size (ie. not
        empyty)
        """
        minSizeSpectra = minSizeSpectra * unitSize
        minSizePhosim = minSizePhosim * unitSize
        success = False
        try:
            spectra_size = os.path.getsize(spectra_tar)
        except:
            spectra_size = False
        try:
            phoSimCat_size = os.path.getsize(phosimInstanceCatalog)
        except:
            phoSimCat_size = False

        if phoSimCat_size and spectra_size:
            success = (phoSimCat_size > minSizePhosim) and (spectra_size > minSizeSpectra)
            if success:
                    untarredInstanceCatalog = phosimInstanceCatalog.split('.gz')[0]
                    if os.path.exists(untarredInstanceCatalog):
                        os.remove(untarredInstanceCatalog)
        return success, phoSimCat_size, spectra_size

    def run(self, filename='validateCompleteness'):
        f = open(filename + '_success.dat', 'w')
        g = open(filename + '_failures.dat', 'w')
        for obsHistID in self.obsHistIDValues:
            phosimInstanceCatalog, spectra = self.filenames(obsHistID,
                                                            self.prefix)
            success, phosimSize, spectraSize = self.validateSizes(phosimInstanceCatalog=phosimInstanceCatalog, spectra_tar=spectra, unitSize=self.MegaByte)
            if success:
                f.write("{0:d},{1:2.1f},{2:2.1f}\n".format(obsHistID,
                        phosimSize, spectraSize))
            else:
                g.write("{0:d},{1:2.1f},{2:2.1f}\n".format(obsHistID,
                       phosimSize, spectraSize)) 
        f.close()
        g.close()

if __name__=='__main__':
    v = ValidatePhoSimCatalogs.fromRunlog(runlog='FirstSet_obsHistIDs.csv',
                                          obsHistIDrange=[500, 600])
    v.run()
