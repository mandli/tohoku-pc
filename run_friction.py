#!/usr/bin/env python

import os
import sys

import numpy

import clawpack.clawutil.tests as clawtests


class FrictionTest(clawtests.Test):
    r""""""

    def __init__(self, index, values, 
                                contours=(numpy.infty,0.0,-200.0,-numpy.infty)):
        r""""""

        super(FrictionTest, self).__init__()

        self.type = "tohoku"
        self.name = "friction-sensitivity"
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

    def __str__(self):
        output = super(FrictionTest, self).__str__()
        output += "\n  Friction Regions:"
        for (n,region) in enumerate(self.rundata.friction_data.friction_regions):
            output += "\n  Region %s: %s" % (n, region)
        return output



if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'coef_quad.txt')
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # Read in friction test values
    friction_values = numpy.loadtxt(path)

    # Create all tests
    tests = []
    for n in xrange(friction_values.shape[0]):
        tests.append(FrictionTest(n, friction_values[n,:]))
    
    controller = clawtests.TestController(tests)
    controller.run()
