#!/usr/bin/env python
from __future__ import absolute_import, print_function
import argparse
import lsst.daf.persistence as daf_persistence
import lsst.afw.display as afw_display

def list_diffims(butler):
    """
    Use the butler to figure out what data are available
    Parameters
    ----------
    butler : daf_persistence.Butler, used to interogate the data repository
    """
    id_list = []
    subset = butler.subset('deepDiff_differenceExp')
    for dataId in subset.cache:
        if butler.datasetExists('deepDiff_differenceExp', dataId=dataId):
            id_list.append(dataId)
    for i, dataId in enumerate(id_list):
        print("%i: %s"%(i, " ".join(["%s=%s"%(key, value) for key, value in dataId.iteritems()])))

def show_diffim(butler, dataId):
    """
    Construct a display of various difference imaging related views
    Parameters
    ----------
    butler : daf_persistence.Butler, used in interacting with the data repository
    dataId : Dictionary, data identifiers to lookup specific data
    """
    def display_image_and_srcs(display, image, title, *srcs):
        """
        Display an image with a title and up to 4 source catalogs
        Parameters
        ----------
        display : afw_display.Display, used to display image and plot catalogs
        image  afw_image.Image-like, pixel data to send to the display backend
        title  str, title for the display frame
        *srcs  afw_tab;e.SourceCatalogs, points to plot
        """
        if len(srcs) > 4:
            print("WARNING: more than four source catalogs sent.  Only plotting the first four.")
        syms = ['o', '+', 'x', 't']
        colors = ['green', 'red', 'blue', 'white']
        with display.Buffering():
            display.mtv(image, title=title)
        for src, plot_sym, color in zip(srcs, syms, colors):
            for s in src:
                display.dot(plot_sym, s.getX(), s.getY(), size=5, ctype=color)
    display0 = afw_display.getDisplay(frame=0, )
    display0.setMaskTransparency(75)
    display0.scale('linear', 'zscale')
    display1 = afw_display.getDisplay(frame=1)
    display1.setMaskTransparency(75)
    display1.scale('linear', 'zscale')
    display2 = afw_display.getDisplay(frame=2)
    display2.setMaskTransparency(75)
    display2.scale('linear', 'zscale')
    exp = butler.get('calexp', dataId)
    src = butler.get('src', dataId)
    diasrc = butler.get('deepDiff_diaSrc', dataId)
    diffexp = butler.get('deepDiff_differenceExp', dataId)
    display_image_and_srcs(display0, exp, 'Direct', src, diasrc) 
    display_image_and_srcs(display1, diffexp, 'Diffim', src, diasrc) 
    im1 = exp.getMaskedImage().getImage()
    im2 = diffexp.getMaskedImage().getImage()
    im1 -= im2
    display_image_and_srcs(display2, im1, 'Direct - Diffim', src, diasrc) 

def make_dataId(id_list):
    """
    Construct a proper dataId from a list of [key]=[value] strings
    Parameters
    ----------
    id_list : List of str, parsee into the dataId
    Returns
    -------
    dictionary containting data identifiers
    """
    dataId = {}
    for el in id_list:
        parts = el.split('=')
        if not len(parts) == 2:
            # id not in Key=Value syntax
            raise RuntimeError("Not able to parse: --id: %s. Not in [key]=[value] syntax"%
                               " ".join([str(el) for el in id_list]))
        # Try to cast to a number, fall back to string
        try:
            value = float(parts[1])
        except Exception:
            value = str(parts[1])
        dataId[parts[0]] = value
    return dataId

def run(repository, id_list=None, **kwargs):
    """
    Figure out what to do with the inputs and call the appropriate methods
    Parameters
    ----------
    repository : str, path of the data repository
    id_list(optional) : list of str, data identifier parts in [key]=[value] strings.
    **kwargs : Ignored.
    """
    try:
        butler = daf_persistence.Butler(repository)
    except RuntimeError:
        raise RuntimeError('Could not open repository.  Check the path: %s'%repository)
    if not id_list:
        list_diffims(butler)
    else:
        dataId = make_dataId(id_list)
        try:
            if butler.datasetExists('deepDiff_differenceExp', dataId=dataId):
                show_diffim(butler, dataId)
            else:
                raise RuntimeError('Could not load data for id: %s.  Dataset does not exist'%id_list)
        except Exception:
            raise
            '''
            raise RuntimeError("Unable to load data. To list possible data ids run"+
                                   " with repository as only argument")
    
            '''
if __name__ == '__main__':
    description = """******\nVisualize difference images given a repository.
In order to use, make sure a display backend (display_ds9), afw, 
and the correc obs (obs_lsstSim) package setup.

If using DS9, make sure it is in your $PATH.

--------------
Frame 0: Direct
Frame 1: Difference
Frame 2: Difference + Direct

In all frames DIA sources are plotted with the red plus, and direct sources in green circles
******
"""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('repository', type=str,
                        help="Data repository to open.\n**List data if no other arguments are supplied.**")
    parser.add_argument('--id', dest='id_list', type=str, nargs='+',
                        help='Id for data to fetch: i.e. --id visit=335 sensor=1,1')
    args = parser.parse_args()
    args = args.__dict__
    run(**args)
