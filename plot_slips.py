#!/usr/bin/env python

import sys

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.dtopotools as dtopotools

def plot_deformation(fault):

    x = numpy.linspace(140.5, 145, (145.0 - 140.5) / 0.05)
    y = numpy.linspace(35, 41, (41.0 - 35.0) / 0.05)
    fault.create_dtopography(x, y)

    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)

    fault.dtopo.plot_dZ_colors(1.0, axes=axes)

    return fig

def plot_fault(fault):
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)

    cmap = plt.get_cmap("YlOrRd")
    fault.plot_subfaults(axes=axes, slip_color=True, cmap_slip=cmap, 
                              cmin_slip=0.0, cmax_slip=30.0,
                              plot_rake=True)
    axes.set_title("$M_o = %s$, $M_w = %s$" % (str(fault.Mo()), str(fault.Mw())))
    fig.savefig("fault_slip.png")

    fig = plot_deformation(fault)
    fig.savefig("fault_deformation.png")

    return fig


def plot_UCSB_fault(path='./UCSB_model3_subfault.txt'):

    fault = dtopotools.UCSBFault(path)

    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)

    cmap = plt.get_cmap("YlOrRd")
    fault.plot_subfaults(axes=axes, slip_color=True, cmap_slip=cmap, 
                              cmin_slip=0.0, cmax_slip=60.0,
                              plot_rake=False)

    axes.set_title("$M_o = %s$, $M_w = %s$" % (str(fault.Mo()), str(fault.Mw())))
    fig.savefig("UCSB_fault_slip.png")

    fig = plot_deformation(fault)
    fig.savefig("UCSB_deformation.png")
    
    return fig


def create_fault(slips):
    # Comparison Fault System
    UCSB_fault = dtopotools.UCSBFault('./UCSB_model3_subfault.txt')

    # Use data from the reconstruced UCSB fault to setup our fault system
    # Calculate average quantities across all subfaults
    ave_rake = 0.0
    ave_strike = 0.0
    ave_slip = 0.0
    for subfault in UCSB_fault.subfaults:
        ave_rake = subfault.rake
        ave_strike = subfault.strike
        ave_slip = subfault.slip

    ave_rake /= len(UCSB_fault.subfaults)
    ave_strike /= len(UCSB_fault.subfaults)
    ave_slip /= len(UCSB_fault.subfaults)

    # Base subfault
    base_subfault = dtopotools.SubFault()
    base_subfault.strike = 198.0
    base_subfault.length = 19 * 25.0 * 1000.0
    base_subfault.width = 10 * 20.0 * 1000.0
    base_subfault.depth = 7.50520 * 1000.0
    base_subfault.slip = ave_slip
    base_subfault.rake = 90.0
    base_subfault.dip = 10.0
    base_subfault.latitude = 37.64165
    base_subfault.longitude = 143.72745
    base_subfault.coordinate_specification = "top center"

    # Create base subdivided fault
    fault = dtopotools.SubdividedPlaneFault(base_subfault, nstrike=3, ndip=2)

    for (k, subfault) in enumerate(fault.subfaults):
        subfault.slip = slips[k]

    return fault


if __name__ == '__main__':
    if len(sys.argv) == 7:
        slips = [float(slip) for slip in sys.argv[1:]]
    else:
        slips = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]

    fault = create_fault(slips)
    fig = plot_fault(fault)
    fig = plot_UCSB_fault()

    plt.show()