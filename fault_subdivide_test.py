#!/usr/bin/env python

from __future__ import print_function

import matplotlib.pyplot as plt

import clawpack.geoclaw.dtopotools as dtopotools

# Comparison Fault System
UCSB_fault = dtopotools.UCSBFault('./UCSB_model3_subfault.txt')

# Use data from the reconstruced UCSB fault to setup our fault system
# Calculate average quantities across all subfaults
ave_rake = 0.0
ave_strike = 0.0
ave_slip = 0.0
for subfault in UCSB_fault.subfaults:
    ave_rake += subfault.rake
    ave_strike += subfault.strike
    ave_slip += subfault.slip

ave_rake /= len(UCSB_fault.subfaults)
ave_strike /= len(UCSB_fault.subfaults)
ave_slip /= len(UCSB_fault.subfaults)
print("Averages:")
print("  Rake   = %s" % ave_rake)
print("  Strike = %s" % ave_strike)
print("  Slip   = %s" % ave_slip)

# Base subfault - based on reconstruction by UCSB
# http://www.geol.ucsb.edu/faculty/ji/big_earthquakes/2011/03/0311_v3/Honshu.html
#
subfault = dtopotools.SubFault()
subfault.strike = 198.0
subfault.length = 19 * 25.0 * 1000.0
subfault.width = 10 * 20.0 * 1000.0
subfault.depth = 7.50520 * 1000.0
subfault.slip = ave_slip
subfault.rake = ave_rake
subfault.dip = 10.0
subfault.latitude = 37.64165
subfault.longitude = 143.72745
subfault.coordinate_specification = "top center"

import os
fault = dtopotools.SubdividedPlaneFault(subfault)
x, y = fault.create_dtopo_xy()
dtopo = fault.create_dtopography(x, y)
dtopo.write(path=os.path.join(os.getcwd(), "fault.tt3"), dtopo_type=3)

# Plot results
fig = plt.figure()
axes = fig.add_subplot(121)
UCSB_fault.plot_subfaults(axes, slip_color=True, cmin_slip=0.0, cmax_slip=60.0)
axes = fig.add_subplot(122)
fault.plot_subfaults(axes, slip_color=True, cmin_slip=0.0, cmax_slip=60.0)

plt.show()

