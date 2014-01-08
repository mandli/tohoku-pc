#!/usr/bin/env python

import os
import sys

import numpy

import batch

class FrictionJob(batch.Job):
    r""""""

    def __init__(self, index, values, 
                       source_path='$SRC/tohoku2011-paper1/sources/Ammon.txydz',
                       contours=(numpy.infty,0.0,-200.0,-numpy.infty)):
        r""""""

        super(FrictionJob, self).__init__()

        self.source_path = os.path.expandvars(source_path)

        self.type = "tohoku"
        self.name = "friction-sensitivity-%s" % \
                        os.path.split(os.path.splitext(self.source_path)[0])[-1]
        self.prefix = "fric_%s" % (str(index))
        self.executable = 'xgeoclaw'

        # Data objects
        import setrun
        self.rundata = setrun.setrun()

        # Set variable friction
        self.rundata.friction_data.variable_friction = True

        # Region based friction
        self.rundata.friction_data.friction_regions.append([
                       self.rundata.clawdata.lower, self.rundata.clawdata.upper,
                       contours, values])

        # Set earthquake source model
        dtopo_data = self.rundata.dtopo_data
        dtopo_data.dtopofiles.append([1, 4, 4, self.source_path])

    def __str__(self):
        output = super(FrictionJob, self).__str__()
        output += "\n  Source model: %s" % self.source_path
        output += "\n  Friction Regions:"
        for (n,region) in enumerate(self.rundata.friction_data.friction_regions):
            output += "\n    Region %s: %s" % (n, region)
        return output



if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'coef_quad.txt')
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # source_path = '$SRC/tohoku2011-paper1/sources/Ammon.txydz'
    source_path = os.path.abspath(os.path.join(os.getcwd(),'saito.xyzt'))

    # Read in friction test values
    friction_values = numpy.loadtxt(path)

    # Create all jobs
    jobs = []
    for n in xrange(friction_values.shape[0]):
        jobs.append(FrictionJob(n, friction_values[n,:], source_path))
    
    controller = batch.BatchController(jobs)
    # controller.run()
    print controller
