#!/usr/bin/env python

import re

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.dtopotools as dtopotools

class HayesSubfault(dtopotools.Fault):
    r""""""

    def __init__(self, path=None, **kwargs):

        self.num_cells = [None, None]

        super(HayesSubfault, self).__init__()

        if path is not None:
            self.read(path, **kwargs)


    def read(self, path, rupture_type="static"):
        r"""Read in subfault specification at *path*.

        Creates a list of subfaults from the subfault specification file at
        *path*.

        Subfault format contains info for dynamic rupture, so can specify 
        rupture_type = 'static' or 'dynamic'

        """

        self.rupture_type = rupture_type

        # Read header of file
        regexp_dx = re.compile(r"Dx=[ ]*(?P<dx>[^k]*)")
        regexp_dy = re.compile(r"Dy=[ ]*(?P<dy>[^k]*)")
        regexp_nx = re.compile(r"nx[^=]*=[ ]*(?P<nx>[^D]*)")
        regexp_ny = re.compile(r"ny[^=]*=[ ]*(?P<ny>[^D]*)")
        found_subfault_discretization = False
        found_subfault_boundary = False
        header_lines = 0
        with open(path, 'r') as subfault_file:
            # Find fault secgment discretization
            for (n,line) in enumerate(subfault_file):
                result_dx = regexp_dx.search(line)
                result_dy = regexp_dy.search(line)
                result_nx = regexp_nx.search(line)
                result_ny = regexp_ny.search(line)

                if result_dx and result_dy:
                    dx = float(result_dx.group('dx'))
                    dy = float(result_dy.group('dy'))
                    self.num_cells[0] = int(result_nx.group('nx'))
                    self.num_cells[1] = int(result_ny.group('ny'))
                    found_subfault_discretization = True
                    break
            header_lines += n

            # Parse boundary
            in_boundary_block = False
            boundary_data = []
            for (n,line) in enumerate(subfault_file):
                if line[0].strip() == "#":
                    if in_boundary_block and len(boundary_data) == 5:
                        found_subfault_boundary = True
                        break
                else:
                    in_boundary_block = True
                    boundary_data.append([float(value) for value in line.split()])

        # Assume that there is a column label right underneath the boundary
        # specification
        header_lines += n + 2

        # Check to make sure last boundary point matches, then throw away
        if boundary_data[0] != boundary_data[4]:
            raise ValueError("Boundary specified incomplete: ",
                             "%s" % boundary_data)


        if not (found_subfault_boundary and found_subfault_discretization):
            raise ValueError("Could not find base fault characteristics in ",
                             "subfault specification file at %s." % path)

        # Calculate center of fault

        column_map = {"latitude":0, "longitude":1, "depth":2, "slip":3,
                       "rake":4, "strike":5, "dip":6, "rupture_time":7,
                       "rise_time":8}#, "rise_time_ending":9, "mu":10}
        defaults = {"length":dx, "width":dy}
        input_units = {"slip":"cm", "depth":"km", 'mu':"dyne/cm^2",
                                   "length":"km", "width":"km"}

        super(HayesSubfault, self).read(path, column_map, skiprows=header_lines,
                                coordinate_specification="centroid",
                                input_units=input_units, defaults=defaults)


class WeiSubfault(dtopotools.Fault):
    r""""""

    def __init__(self, path=None, **kwargs):

        self.num_cells = [None, None]

        super(WeiSubfault, self).__init__()

        if path is not None:
            self.read(path, **kwargs)


    def read(self, path, rupture_type="static"):
        r"""Read in subfault specification at *path*.

        Creates a list of subfaults from the subfault specification file at
        *path*.

        Subfault format contains info for dynamic rupture, so can specify 
        rupture_type = 'static' or 'dynamic'

        """

        self.rupture_type = rupture_type

        # Read header of file
        regexp_dx = re.compile(r"Dx=[ ]*(?P<dx>[^k]*)")
        regexp_dy = re.compile(r"Dy=[ ]*(?P<dy>[^k]*)")
        regexp_nx = re.compile(r"nx[^=]*=[ ]*(?P<nx>[^D]*)")
        regexp_ny = re.compile(r"ny[^=]*=[ ]*(?P<ny>[^D]*)")
        found_subfault_discretization = False
        found_subfault_boundary = False
        header_lines = 0
        with open(path, 'r') as subfault_file:
            # Find fault secgment discretization
            for (n,line) in enumerate(subfault_file):
                result_dx = regexp_dx.search(line)
                result_dy = regexp_dy.search(line)
                result_nx = regexp_nx.search(line)
                result_ny = regexp_ny.search(line)

                if result_dx and result_dy:
                    dx = float(result_dx.group('dx'))
                    dy = float(result_dy.group('dy'))
                    self.num_cells[0] = int(result_nx.group('nx'))
                    self.num_cells[1] = int(result_ny.group('ny'))
                    found_subfault_discretization = True
                    break
            header_lines += n

            # Parse boundary
            in_boundary_block = False
            boundary_data = []
            for (n,line) in enumerate(subfault_file):
                if line[0].strip() == "#":
                    if in_boundary_block and len(boundary_data) == 5:
                        found_subfault_boundary = True
                        break
                else:
                    in_boundary_block = True
                    boundary_data.append([float(value) for value in line.split()])

        # Assume that there is a column label right underneath the boundary
        # specification
        header_lines += n + 2

        # Check to make sure last boundary point matches, then throw away
        if boundary_data[0] != boundary_data[4]:
            raise ValueError("Boundary specified incomplete: ",
                             "%s" % boundary_data)


        if not (found_subfault_boundary and found_subfault_discretization):
            raise ValueError("Could not find base fault characteristics in ",
                             "subfault specification file at %s." % path)

        # Calculate center of fault

        column_map = {"latitude":1, "longitude":0, "depth":2, "slip":3,
                       "rake":4, "strike":5, "dip":6}
        defaults = {"length":dx, "width":dy}
        input_units = {"slip":"cm", "depth":"km", 'mu':"dyne/cm^2",
                                   "length":"km", "width":"km"}

        super(WeiSubfault, self).read(path, column_map, skiprows=header_lines,
                                coordinate_specification="centroid",
                                input_units=input_units, defaults=defaults)


def extract_extreme_slips(fault):

    min_slip = numpy.infty
    max_slip = 0.0
    for subfault in fault.subfaults:
        min_slip = min(min_slip, subfault.slip)
        max_slip = max(max_slip, subfault.slip)

    return min_slip, max_slip


faults = [HayesSubfault("./hayes_subfault.txt"), 
          dtopotools.UCSBFault("./Shao_et_al_subfault.txt"), 
          WeiSubfault("Wei_et_al_subfault.txt")]

min_slip = numpy.infty
max_slip = 0.0
for [n, fault] in enumerate(faults):
    fault_min_slip, fault_max_slip = extract_extreme_slips(fault)
    print "Fault[%s]" % n
    print "  slip(min, max) = (%s, %s)" % (fault_min_slip, fault_max_slip)
    min_slip = min(min_slip, fault_min_slip)
    max_slip = max(max_slip, fault_max_slip)

print min_slip, max_slip


