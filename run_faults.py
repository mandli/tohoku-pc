#!/usr/bin/env python

"""Run specified faults in the provided CSV file."""

import os
import sys

import numpy

import batch

class FaultJob(batch.Job):

    r"""Job describing a single Okada based fault relization.

    Fault parameterization is:

    """

    def __init__(self, fault_params):        
        r"""
        Initialize a FaultJob object.
        
        See :class:`FaultJob` for full documentation
        
        """ 

        super(FaultJob, self).__init__()

        self.fault_params = fault_params

        self.type = "tohoku"
        self.name = "okada-fault-PC-analysis"
        self.prefix = "fault_%s" % (str(self.fault_params))
        self.executable = 'xgeoclaw'

        # Data objects
        import setrun
        self.rundata = setrun.setrun()

    def __str__(self):
        output = super(FaultJob, self).__str__()
        output += "\n  Fault Parameters:"
        return output

    def write_data(self):

        # Write other data files
        super(FaultJob, self).write_data()

        # Write out fault parameter file




if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'coef_quad.txt')
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # Load fault parameters
    fault_values = numpy.loadtxt(path)

    # Create all jobs
    jobs = []
    for fault_params in xrange(fault_values.shape[0]):
        jobs.append(FaultJob(fault_params))
    
    controller = batch.BatchController(jobs)
    # controller.run()
    print controller
