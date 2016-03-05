from analyseICat import *
from calc_snr import *
from cleanupspectra import *

# It's hard to setup lsst-sims cleanly with conda, so we protect ourselves
# to some extent with the following try/except clauses. This only postpones
# the inevitable, but it shoudl allow at least some Twinkles code to run. 
try:
    from generatePhosimInput import generatePhosimInput
except ImportError, eobj:
    print "Error importing generatePhosimInput", eobj
from InstcatGenerationBooKeeping import *
try:
    from InstcatGenerator import InstcatFactory, InstcatFactory
except ImportError, eobj:
    print "Error importing InstcatGenerator", eobj
try:
    from sprinkler import sprinklerCompound, sprinkler
except ImportError, eobj:
    print "Error importing sprinkler", eobj
try:
    from twinklesCatalogDefs import TwinklesCatalogZPoint
except ImportError, eobj:
    print "Error importing twinklesCatalogDefs", eobj
try:
    from twinklesVariabilityMixins import TimeDelayVariability, VariabilityTwinkles
except ImportError, eobj:
        print "Error importing twinklesVariabilityMixins", eobj

from PostageStampMaker import PostageStampMaker, create_postage_stamps
from Display import render_fits_image
