import unittest
import numpy as np

from lsst.sims.utils import ObservationMetaData
from lsst.sims.utils import cartesianFromSpherical
from lsst.sims.catUtils.mixins import PhoSimAstrometryBase
from desc.twinkles import _rePrecess

class PrecessionTestCase(unittest.TestCase):

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

if __name__ == "__main__":
    unittest.main()
