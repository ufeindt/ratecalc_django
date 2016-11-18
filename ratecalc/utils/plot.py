import numpy as np

import cStringIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def plot_lightcurve(phase, mag):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    ax.plot(phase, mag)
    
    ax.set_xlim(np.min(phase), np.max(phase))
    ax.set_ylim(ax.get_ylim()[::-1])

    ax.set_xlabel(r'$t - t_0 \mathrm{[days]}$', fontsize='x-large')
    ax.set_ylabel(r'mag', fontsize='x-large')

    ax.grid(True)
    
    return make_svg_str(fig)

def plot_expected(mag, n):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    ax.plot(mag, n)
    
    ax.set_xlim(np.min(mag), np.max(mag))
    ax.set_yscale('log')

    ax.set_xlabel('Limiting magnitude', fontsize='x-large')
    ax.set_ylabel('# expected transients per year', fontsize='x-large')

    ax.grid(True)
    
    return make_svg_str(fig)

def plot_redshift(z, n, width=0.01):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    ax.bar(z-width/2., n, width=width)
    
    ax.set_xlim(np.min(z)-width/2., np.max(z)+width/2.)

    ax.set_xlabel('Redshift', fontsize='x-large')
    ax.set_ylabel('# expected transients per year', fontsize='x-large')

    ax.grid(True)
    
    return make_svg_str(fig)
    
def make_svg_str(fig):
    canvas = FigureCanvas(fig)

    graphic = cStringIO.StringIO()
    fig.savefig(graphic, format='svg', bbox_inches='tight')

    return graphic.getvalue()