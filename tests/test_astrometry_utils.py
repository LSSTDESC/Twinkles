from __future__ import with_statement
import unittest
import numpy as np
import os

from lsst.sims.utils import ObservationMetaData, raDecFromAltAz
from lsst.sims.utils import cartesianFromSpherical
from lsst.sims.catUtils.mixins import PhoSimAstrometryBase
from lsst.utils import getPackageDir
from lsst.sims.catalogs.db import fileDBObject
from lsst.sims.catalogs.definitions import InstanceCatalog
from lsst.sims.catalogs.decorators import compound
from lsst.sims.catUtils.mixins import PhoSimAstrometryStars
from lsst.sims.utils import _icrsFromObserved
from desc.twinkles import _rePrecess, icrsFromPhoSim
from desc.twinkles import StarCacheDBObj

class PrecessionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        This method creates a dummy database that looks like our
        cache of stars from fatboy, but only contains astrometrically
        relevant quantities, ignoring photometrically relevant quantities.
        """
        cls.scratch_dir = os.path.join(getPackageDir('twinkles'),
                                       'tests', 'scratchSpace')

        rng = np.random.RandomState(81822)
        mjd = 59781.2
        ra, dec = raDecFromAltAz(60.0, 112.0, ObservationMetaData(mjd=mjd))

        rot = 12.0
        cls.cat_obs = ObservationMetaData(pointingRA=ra,
                                          pointingDec=dec,
                                          rotSkyPos=rot,
                                          mjd=mjd,
                                          boundType='circle',
                                          boundLength=1.75)

        n_obj = 2000
        rr = rng.random_sample(n_obj)*1.75
        theta = rng.random_sample(n_obj)*2.0*np.pi
        ra_list = ra + rr*np.cos(theta)
        dec_list = dec + rr*np.sin(theta)
        mura_list = (rng.random_sample(n_obj)-0.5)*100.0
        mudec_list = (rng.random_sample(n_obj)-0.5)*100.0
        px_list = rng.random_sample(n_obj)*50.0
        vrad_list = (rng.random_sample(n_obj)-0.5)*600.0

        cat_txt_name = os.path.join(cls.scratch_dir,
                                    'test_stars_cat_source.txt')
        if os.path.exists(cat_txt_name):
            os.unlink(cat_txt_name)

        with open(cat_txt_name, 'w') as output_file:
            for ix, (ra, dec, mura, mudec, px, vrad) in \
            enumerate(zip(ra_list, dec_list, mura_list,
                          mudec_list, px_list, vrad_list)):

                output_file.write('%d;%.16g;%.16g;%.16g;%.16g;%.16g;%.16g\n'
                                  % (ix, ra, dec, mura, mudec, px, vrad))

        dtype = np.dtype([('simobjid', int), ('ra', float), ('decl', float),
                          ('mura', float), ('mudecl', float),
                          ('parallax', float), ('vrad', float)])

        cls.db_name = os.path.join(cls.scratch_dir, 'test_stars_cata_sqlite.db')

        if os.path.exists(cls.db_name):
            os.unlink(cls.db_name)

        fileDBObject(cat_txt_name, database=cls.db_name, dtype=dtype,
                     delimiter=';', driver='sqlite', idColKey='simobjid',
                     runtable='star_cache_table')

        if os.path.exists(cat_txt_name):
            os.unlink(cat_txt_name)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_name):
            os.unlink(cls.db_name)

    def test_re_precess(self):
        """
        Test that _rePrecess undoes the _dePrecess method from
        PhoSimAstrometryBase
        """

        ra = 25.0
        dec = -113.0
        rotSkyPos = 32.1
        mjd = 59571.2
        obs = ObservationMetaData(pointingRA=ra, pointingDec=dec,
                                  rotSkyPos=rotSkyPos, mjd=mjd)

        rng = np.random.RandomState(33)
        n_obj = 1000
        rr = rng.random_sample(n_obj)*3.0
        theta = rng.random_sample(n_obj)*2.0*np.pi
        ra_list = np.radians(ra + rr*np.cos(theta))
        dec_list = np.radians(dec + rr*np.sin(theta))
        ast = PhoSimAstrometryBase()
        ra_precessed, dec_precessed = ast._dePrecess(ra_list, dec_list, obs)
        ra_test, dec_test = _rePrecess(ra_precessed, dec_precessed, obs)

        xyz0 = cartesianFromSpherical(ra_list, dec_list)
        xyz1 = cartesianFromSpherical(ra_test, dec_test)
        for control, test in zip(xyz0, xyz1):
            dd = np.sqrt(np.power(xyz0-xyz1,2).sum())
            self.assertLess(dd, 1.0e-10)

        # try it one at a time
        for ix, (ra_in, dec_in) in enumerate(zip(ra_precessed, dec_precessed)):
            ra_test, dec_test = _rePrecess(ra_in, dec_in, obs)
            xyz0 = cartesianFromSpherical(ra_list[ix], dec_list[ix])
            xyz1 = cartesianFromSpherical(ra_test, dec_test)
            xyz2 = cartesianFromSpherical(ra_precessed[ix], dec_precessed[ix])
            self.assertEqual(xyz0.shape, (3,))
            self.assertEqual(xyz1.shape, (3,))
            dd = np.sqrt(np.power(xyz0-xyz1, 2).sum())
            self.assertLess(dd, 1.0e-10)
            dd2 = np.sqrt(np.power(xyz0-xyz2, 2).sum())
            self.assertGreater(dd2,1.0e-6)

    def test_end_to_end(self):
        """
        Test that we can transform from PhoSim RA, Dec back to
        ICRS RA, Dec
        """

        class testRaDecCat(PhoSimAstrometryStars, InstanceCatalog):
            column_outputs = ['raPhoSim', 'decPhoSim', 'raControl', 'decControl']

            transformations = {'raPhoSim': np.degrees, 'decPhoSim': np.degrees,
                               'raControl': np.degrees, 'decControl': np.degrees}

            @compound('raControl', 'decControl')
            def get_controlCoords(self):
                return _icrsFromObserved(self.column_by_name('raObserved'),
                                         self.column_by_name('decObserved'),
                                         obs_metadata=self.obs_metadata,
                                         epoch=2000.0)

        StarCacheDBObj.database = self.db_name
        db = StarCacheDBObj()
        cat = testRaDecCat(db, obs_metadata=self.cat_obs)
        ct = 0
        for star in cat.iter_catalog():
            ra_test, dec_test = icrsFromPhoSim(star[0], star[1], self.cat_obs)
            xyz0 = cartesianFromSpherical(np.radians(star[2]), np.radians(star[3]))
            xyz1 = cartesianFromSpherical(np.radians(ra_test), np.radians(dec_test))
            dd = np.sqrt(np.power(xyz0-xyz1,2).sum())
            self.assertLess(dd, 1.0e-10)
            ct += 1
        self.assertGreater(ct, 0)

if __name__ == "__main__":
    unittest.main()
