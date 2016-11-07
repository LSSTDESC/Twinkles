from __future__ import absolute_import
import numpy as np
from matplotlib import pyplot as plt
# from astroML.plotting.tools import draw_ellipse
from astroML.plotting import setup_text_plots
# from sklearn.mixture import GMM as skl_GMM

def plot_bic(param_range,bics,lowest_comp):
    plt.clf()
    setup_text_plots(fontsize=16, usetex=True)
    fig = plt.figure(figsize=(12, 6))
    plt.plot(param_range,bics,color='blue',lw=2, marker='o')
    plt.text(lowest_comp, bics.min() * 0.97 + .03 * bics.max(), '*',
             fontsize=14, ha='center')

    plt.xticks(param_range)
    plt.ylim(bics.min() - 0.05 * (bics.max() - bics.min()),
             bics.max() + 0.05 * (bics.max() - bics.min()))
    plt.xlim(param_range.min() - 1, param_range.max() + 1)

    plt.xticks(param_range,fontsize=14)
    plt.yticks(fontsize=14)

    plt.xlabel('Number of components',fontsize=18)
    plt.ylabel('BIC score',fontsize=18)

    plt.show()
