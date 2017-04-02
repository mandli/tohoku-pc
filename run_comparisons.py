#!/usr/bin/env python

"""Run specified faults in the provided CSV file."""

from __future__ import print_function

import sys
import os
import glob

import numpy
import matplotlib.pyplot as plt

import batch

import clawpack.geoclaw.dtopotools as dtopotools
import clawpack.pyclaw.gauges as gauges


def plot_gauge_comparisons(jobs, save=False):
    r"""Plot the gauge comparisons for all of the jobs listed"""

    gauge_ids = [21401, 21413, 21414, 21415, 21419, 52402] # 21418
    time_limits = {}
    tfinal = 6 * 3600.0
    time_limits[21401] = [0, tfinal]
    time_limits[21413] = [0, tfinal]
    time_limits[21414] = [2 * 3600.0, tfinal]
    time_limits[21415] = [2 * 3600.0, tfinal]
    # time_limits[21418] = [0, tfinal]
    time_limits[21419] = [0, 20000.0]
    time_limits[46411] = [7 * 3600.0, tfinal]
    time_limits[52402] = [2 * 3600.0, tfinal]

    offsets = {}
    offsets[21401] = 0.0
    offsets[21413] = 0.0
    offsets[21414] = 0.0
    offsets[21415] = 0.01
    # offsets[21418] = 0.0 # Not found
    offsets[21419] = 0.0
    offsets[46411] = 0.0
    offsets[52402] = 0.0

    # Paths to data
    dart_data_path = os.path.join(os.getcwd(), "dart")
    if os.environ.has_key('DATA_PATH'):
        base_path = os.environ['DATA_PATH']
    else:
        base_path = os.getcwd()
    base_path = os.path.join(os.path.expanduser(base_path), jobs[0].type,
                                                            jobs[0].name)
    print("Loading gauge data from: %s" % base_path)
    for job in jobs:
        if job.prefix == "fault_SIFT":
            sift_path = os.path.join(base_path, "%s_output" % job.prefix)
        elif job.prefix == "fault_inversion":
            inv_path = os.path.join(base_path, "%s_output" % job.prefix)

    # Load DART gauges
    dart_gauges = {}
    for gaugeno in gauge_ids:
        files = glob.glob(os.path.join(dart_data_path, '%s*_notide.txt'
                                                                    % gaugeno))
        if len(files) != 1:
            print("*** Warning: found %s files for gauge number %s"
                                                       % (len(files), gaugeno))
        try:
            fname = files[0]
            dart_gauges[gaugeno] = numpy.loadtxt(fname)
        except:
            pass

    # Plot data
    figures = []
    for (n, gauge_id) in enumerate(gauge_ids):
        fig = plt.figure()
        fig.set_figwidth(fig.get_figwidth() * 2.0)
        axes = fig.add_subplot(1, 1, 1)

        sift_gauge = gauges.GaugeSolution(gauge_id, path=sift_path)
        inv_gauge = gauges.GaugeSolution(gauge_id, path=inv_path)
        print("Loaded gauge %s." % gauge_id)

        # Add model data
        axes.plot(sift_gauge.t / 3600.0, sift_gauge.q[-1, :], 'b', label="SIFT")
        axes.plot(inv_gauge.t / 3600.0, inv_gauge.q[-1, :], 'r', label="Inversion")

        # Add DART data
        axes.plot(dart_gauges[gauge_id][:, 0] / 3600.0,
                  dart_gauges[gauge_id][:, 1] + offsets[gauge_id],
                  'k', label="Observed")

        # Add zero line
        axes.plot((time_limits[gauge_id][0] / 3600.0, time_limits[gauge_id][1] / 3600.0),
                  [0.0, 0.0], 'k--')

        # Constrain time window
        axes.set_xlim((time_limits[gauge_id][0] / 3600.0, time_limits[gauge_id][1] / 3600.0))

        # Add labels
        axes.set_title("Gauge %s" % gauge_id)
        axes.set_xlabel("t (h)")
        axes.set_ylabel("$\eta$ (m)")
        axes.legend()

        figures.append(fig)

        if save:
            fig.savefig("./gauge_comparisons/gauge%s.pdf" % gauge_id)

    return figures


def create_SIFT_fault():

    # Slip definition
    sift_slip = {"kiszb24": 4.66,
                 "kiszb25": 12.23,
                 "kisza26": 26.31,
                 "kiszb26": 21.27,
                 "kisza27": 22.75,
                 "kiszb27": 4.98}

    return dtopotools.SiftFault(sift_slip)


def create_inverted_fault():
    # Create fault
    # Based on UCSB reconstruction and assumption of single subfault
    # Lengths are based on num_fault_segments * dx * m/km in each direction
    #
    # Top edge    Bottom edge
    #   a ----------- b          ^ 
    #   |             |          |         ^
    #   |             |          |         |
    #   |             |          |         | along-strike direction
    #   |             |          |         |
    #   0------1------2          | length  |
    #   |             |          |
    #   |             |          |
    #   |             |          |
    #   |             |          |
    #   d ----------- c          v
    #   <------------->
    #       width
    # <-- up dip direction
    #
    #  Given
    #      Long            Lat             Depth
    #  a = 144.56380       39.66720        7.50520
    #  b = 140.76530       36.15960       41.96770
    #  c = 142.43800       40.21080       41.96770
    #  d = 142.89110       35.61610        7.50520
    #  Computed
    #      Long            Lat             Depth
    #  0 = 143.72745       37.64165        7.50520
    # Comparison Fault System
    UCSB_fault = dtopotools.UCSBFault('./UCSB_model3_subfault.txt')

    slips = [2.7, 23, 0.3, 6.5, 21.5, 0.3]

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
    fault = dtopotools.SubdividedPlaneFault(base_subfault,
                                                 nstrike=3, ndip=2)
    for (k, subfault) in enumerate(fault.subfaults):
        subfault.slip = slips[k]

    return fault


class FaultJob(batch.Job):

    r"""Job describing a single Okada based fault relization.

    Fault parameterization is:

    """

    # Class instances used for plotting using the same bounds
    cmin_slip = 0.0
    cmax_slip = 60.0

    def __init__(self, fault, name=""): 
        r"""
        Initialize a FaultJob object.
        
        See :class:`FaultJob` for full documentation
        
        """ 

        super(FaultJob, self).__init__()

        self.type = "tsunami"
        self.name = "final-tohoku-inversions"
        self.prefix = "fault_%s" % name
        self.executable = 'xgeoclaw'

        # Data objects
        import setrun
        self.rundata = setrun.setrun()

        # No variable friction for the time being
        self.rundata.friction_data.variable_friction = False

        # Replace dtopo file with our own
        self.dtopo_path = 'fault_%s.tt3' % name
        self.rundata.dtopo_data.dtopofiles = [[3, 4, 4, self.dtopo_path]]

        self.fault = fault


    def write_data_objects(self):

        # Create dtopo file
        x, y = self.fault.create_dtopo_xy()
        dtopo = self.fault.create_dtopography(x, y)
        dtopo.write(path=self.dtopo_path, dtopo_type=3)

        # Plot fault here
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)

        cmap = plt.get_cmap("YlOrRd")
        self.fault.plot_subfaults(axes=axes, slip_color=True, cmap_slip=cmap, 
                                  cmin_slip=FaultJob.cmin_slip, cmax_slip=FaultJob.cmax_slip,
                                  plot_rake=True)
        axes.set_title("$M_o = %s$, $M_w = %s$" % (str(self.fault.Mo()), str(self.fault.Mw())))
        fig.savefig("fault_slip.png")

        # Write other data files
        super(FaultJob, self).write_data_objects()


if __name__ == '__main__':

    run = False
    plot = False
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "run":
            run = True
        elif sys.argv[1].lower() == "plot":
            plot = True

    jobs = []
    jobs.append(FaultJob(create_inverted_fault(), name="inversion"))
    jobs.append(FaultJob(create_SIFT_fault(), name="SIFT"))

    controller = batch.BatchController(jobs)
    controller.plot = True
    print(controller)
    if run:
        controller.run()

    if plot:
        figures = plot_gauge_comparisons(jobs, save=True)
