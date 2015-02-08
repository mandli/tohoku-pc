#!/usr/bin/env python

"""Run specified faults in the provided CSV file."""

from __future__ import print_function

import sys
import os

import numpy
import matplotlib.pyplot as plt

import batch

import clawpack.geoclaw.dtopotools as dtopotools

# def calculate_1parameter_quadrature(param_range):
#     r"""Calculates quadrature in parameter space from the stochastic space

#     Stochastic space is [-1, 1].  This is specific for 6 gaussian qadrature 
#     nodes.  Input needed is the minimum and maximum of the range of the 
#     parameter.
#     """
#     quadrature_weights = numpy.array([-0.932469514203152,
#                                       -0.661209386466264,
#                                       -0.238619186083197,
#                                        0.238619186083197,
#                                        0.661209386466264,
#                                        0.932469514203152])

#     mu = (param_range[0] + param_range[1]) / 2
#     sigma = (param_range[1] - param_range[0]) / 2

#     return mu + sigma * quadrature_weights


# Fault Parameter Search
#  Fault Inversions
#
#
#

class FaultJob(batch.Job):

    r"""Job describing a single Okada based fault relization.

    Fault parameterization is:

    """

    # Class instances used for plotting using the same bounds
    cmin_slip = 0.0
    cmax_slip = 120.0

    def __init__(self, slips, run_number=1): 
        r"""
        Initialize a FaultJob object.
        
        See :class:`FaultJob` for full documentation
        
        """ 

        super(FaultJob, self).__init__()

        self.run_number = run_number

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
        self.base_subfault = dtopotools.SubFault()
        self.base_subfault.strike = 198.0
        self.base_subfault.length = 19 * 25.0 * 1000.0
        self.base_subfault.width = 10 * 20.0 * 1000.0
        self.base_subfault.depth = 7.50520 * 1000.0
        self.base_subfault.slip = ave_slip
        self.base_subfault.rake = 90.0
        self.base_subfault.dip = 10.0
        self.base_subfault.latitude = 37.64165
        self.base_subfault.longitude = 143.72745
        self.base_subfault.coordinate_specification = "top center"

        # Create base subdivided fault
        self.fault = dtopotools.SubdividedPlaneFault(self.base_subfault, 
                                                     nstrike=3, ndip=2)
        for (k, subfault) in enumerate(self.fault.subfaults):
            subfault.slip = slips[k]

        self.type = "tohoku"
        self.name = "okada-fault-PC-analysis"
        self.prefix = "fault_%s" % self.run_number
        self.executable = 'xgeoclaw'

        # Data objects
        import setrun
        self.rundata = setrun.setrun()
        
        # No variable friction for the time being
        self.rundata.friction_data.variable_friction = False

        # Replace dtopo file with our own
        self.dtopo_path = 'fault_s%s.tt3' % self.base_subfault.slip
        self.rundata.dtopo_data.dtopofiles = [[3, 4, 4, self.dtopo_path]]


    def __str__(self):
        output = super(FaultJob, self).__str__()
        output += "\n  Fault Parameters:\n"
        output += "      run_number = %s\n" % self.run_number
        output += "      slips = "
        for subfault in self.fault.subfaults:
            output += "%s " % subfault.slip
        output += "\n"
        return output


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
    
    # If a file is found on the command line, use that to calculate the 
    # quadrature points, otherwise calculate it given a default range
    if len(sys.argv) > 1:
        path = sys.argv[1]

        # Load fault parameters
        slips = numpy.loadtxt(path)
    else:
        slips = numpy.loadtxt("./slip_quads.txt")
        # slip_range = (0.0, 120.0)
        # slips = calculate_quadrature(slip_range)
    
    # Create all jobs
    path = os.path.join(os.environ.get('DATA_PATH', os.getcwd()), 
                "tohoku", "okada-fault-PC-analysis",
                    "run_log.txt")

    # Find minimum and maximum slips for plotting of the faults
    FaultJob.cmin_slip = numpy.min(slips)
    FaultJob.cmax_slip = numpy.max(slips)

    with open(path, 'w') as run_log_file: 
        jobs = []
        for (n, slip) in enumerate(slips):
            run_log_file.write("%s %s\n" % (n, ' '.join([str(x) for x in slip])))
            jobs.append(FaultJob(slip, run_number=n))
            break

    controller = batch.BatchController(jobs)
    print(controller)
    controller.run()
