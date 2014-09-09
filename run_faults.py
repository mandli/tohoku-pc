#!/usr/bin/env python

"""Run specified faults in the provided CSV file."""

from __future__ import print_function

import sys

import numpy

import batch

import clawpack.geoclaw.dtopotools as dtopotools

def calculate_quadrature(param_range):
    r"""Calculates quadrature in parameter space from the stochastic space

    Stochastic space is [-1, 1].  This is specific for 6 gaussian qadrature 
    nodes.  Input needed is the minimum and maximum of the range of the 
    parameter.
    """
    quadrature_weights = numpy.array([-0.932469514203152,
                                      -0.661209386466264,
                                      -0.238619186083197,
                                       0.238619186083197,
                                       0.661209386466264,
                                       0.932469514203152])

    mu = (param_range[0] + param_range[1]) / 2
    sigma = (param_range[1] - param_range[0]) / 2

    return mu + sigma * quadrature_weights

class FaultJob(batch.Job):

    r"""Job describing a single Okada based fault relization.

    Fault parameterization is:

    """

    def __init__(self, slip):        
        r"""
        Initialize a FaultJob object.
        
        See :class:`FaultJob` for full documentation
        
        """ 

        super(FaultJob, self).__init__()

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
        self.base_subfault.slip = slip
        self.base_subfault.rake = ave_rake
        self.base_subfault.dip = 10.0
        self.base_subfault.latitude = 37.64165
        self.base_subfault.longitude = 143.72745
        self.base_subfault.coordinate_specification = "top center"

        # Create base subdivided fault
        self.fault = dtopotools.SubdividedPlaneFault(self.base_subfault)

        self.type = "tohoku"
        self.name = "okada-fault-PC-analysis"
        self.prefix = "fault_s%s" % (self.base_subfault.slip)
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
        output += "      slip=%s\n" % self.base_subfault.slip
        return output


    def write_data_objects(self):

        # Create dtopo file
        x, y = self.fault.create_dtopo_xy()
        dtopo = self.fault.create_dtopography(x, y)
        dtopo.write(path=self.dtopo_path, dtopo_type=3)

        # Write other data files
        super(FaultJob, self).write_data_objects()


if __name__ == '__main__':
    
    # If a file is found on the command line, use that to calculate the 
    # quadrature points, otherwise calculate it given a default range
    if len(sys.argv) > 1:
        path = sys.argv[1]

        # Load fault parameters
        slips = numpy.loadtxst(path)
    else:
        slip_range = (0.0, 120.0)
        slips = calculate_quadrature(slip_range)
    
    # Create all jobs
    jobs = []
    for slip in slips:
        jobs.append(FaultJob(slip))

    controller = batch.BatchController(jobs)
    controller.run()
