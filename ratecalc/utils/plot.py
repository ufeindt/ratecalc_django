import numpy as np

import cStringIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def plot_lightcurve(phase, mags, labels, mag_cut=10):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    for m_, l_ in zip(mags, labels):
        ax.plot(phase, m_, label=l_)
    
    ax.set_xlim(np.min(phase), np.max(phase))

    y_min = min([min(m_[~np.isnan(m_)]) for m_ in mags]) - 1
    y_max = max([max(m_[~np.isnan(m_)]) for m_ in mags])
    
    if y_max - y_min > mag_cut:
        y_max = y_min + mag_cut

    ax.set_ylim(y_max, y_min)

    ax.set_xlabel(r'$t - t_0 \mathrm{[days]}$', fontsize='x-large')
    ax.set_ylabel(r'mag', fontsize='x-large')

    ax.legend(loc='upper center',
              bbox_to_anchor=(.5, 1.15),
              ncol=len(labels))
    
    ax.grid(True)
    
    return make_svg_str(fig)

def plot_expected(mag, n, labels):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    for n_, l_ in zip(n, labels):
        ax.plot(mag, n_, label=l_)
    
    ax.set_xlim(np.min(mag), np.max(mag))
    ax.set_yscale('log')

    ax.set_xlabel('Limiting magnitude', fontsize='x-large')
    ax.set_ylabel('# expected transients', fontsize='x-large')

    ax.legend(loc='upper center',
              bbox_to_anchor=(.5, 1.15),
              ncol=len(labels))
    
    ax.grid(True)
    
    return make_svg_str(fig)

def plot_redshift(z, n, width=0.01):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    width = z[1] - z[0]
    ax.bar(z-width/2., n, width=width)
    
    ax.set_xlim(np.min(z)-width/2., np.max(z)+width/2.)

    ax.set_xlabel('Redshift', fontsize='x-large')
    ax.set_ylabel('# expected transients', fontsize='x-large')

    ax.grid(True)
    
    return make_svg_str(fig)
    
def make_svg_str(fig):
    canvas = FigureCanvas(fig)

    graphic = cStringIO.StringIO()
    fig.savefig(graphic, format='svg', bbox_inches='tight')

    return graphic.getvalue()