import pandas as pd
import sys, os
import tarfile
import gzip

class ValidatePhoSimCatalogs(object):
    MegaByte = 1024*1024
    def __init__(self,
                 obsHistIDValues,
		 prefix='InstanceCatalogs/phosim_input_'):
         self.obsHistIDValues = obsHistIDValues
         self.prefix=prefix

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
        basename =  prefix + str(obsHistID) 
        spectra_tar = basename + '.tar.gz'
        phosimInstanceCatalog = basename + '.txt.gz'
        return phosimInstanceCatalog, spectra_tar

    @staticmethod
    def listSpectraFromPhosimInstanceCatalog(phosimInstanceCatalog,
                                            filePrefix='spectra_files'):
        """
        obtain a list of filenames of SN spectra mentioned in a phosim Instance
        catalog.

        Parameters
        ---------- 
        phosimInstanceCatalog: string, mandatory
            absolute filename for phosimInstanceCatalog
        filePrefix : string, optional, default to 'spectra_files'
            This function assumes that all SN spectra have the same
            prefix 
        """
        if phosimInstanceCatalog.endswith('gz'):
            with  gzip.open(phosimInstanceCatalog, 'r') as f:
                contents = f.read()
        elif phosimInstanceCatalog.endswith('txt'):
            with open(phosimInstanceCatalog, 'r') as f:
                contents = f.read()
        else:
            raise ValueError('Not implemented: handling files with ending string', phosimInstanceCatalog)
        fnames = [ee for ee in contents.split() if filePrefix in ee]
        return fnames


    @staticmethod
    def listTarredSpectra(tarredspectra):
        """
        """
        t =  tarfile.open(tarredspectra, 'r|gz')
        fnames = t.getnames()
        return fnames

    @staticmethod
    def compareFilenames(phosimInstanceCatalog, tarredspectra):

        phosimspectra = ValidatePhoSimCatalogs.listSpectraFromPhosimInstanceCatalog(phosimInstanceCatalog)
        tarredspecs = ValidatePhoSimCatalogs.listTarredSpectra(tarredspectra)
        pss = set(phosimspectra)
        ts = set(tarredspecs)
        return ts == pss, pss - ts, ts - pss


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
	    success  = (phoSimCat_size > minSizePhosim) and (spectra_size > minSizeSpectra)
            if success:
                    untarredInstanceCatalog = phosimInstanceCatalog.split('.gz')[0]
                    if os.path.exists(untarredInstanceCatalog):
                        os.remove(untarredInstanceCatalog)
        return success, phoSimCat_size, spectra_size, unitSize

	

    def run(self, filename='validateCompleteness'):
        f = open(filename + '_success.dat', 'w')
        g = open(filename +'_failures.dat', 'w')
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
#
#                
#
# 
#def filenames(obsHistID, prefix='InstanceCatalogs/phosim_input_'):
#    """
#    return the filenames for the phosim instance catalog and the spectra tar
#    ball corresponding to the obsHistID.
#
#    """
#    basename =  prefix + str(obsHistID) 
#    spectra_tar = basename + 'tar.gz'
#    phosimInstanceCatalog = basename + '.txt.gz'
#
#    return phosimInstanceCatalog, specta_tar
#
#
