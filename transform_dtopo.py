#!/usr/bin/env python

import sys
import os

import numpy
import scipy.interpolate as interp
import matplotlib.pyplot as plt

import clawpack.visclaw.colormaps as colormaps

def read_deformation(path):
    r""""""

    data = numpy.loadtxt(path)

    x = data[:,0]
    y = data[:,1]
    z = data[:,2]

    # Find maximum extents and minimum distance between points
    extents = [numpy.min(x), numpy.min(y), numpy.max(x), numpy.max(y)]

    return extents, x, y, z


def project_deformation(extents, x, y, z):
    r""""""

    # Construct new grid
    num_cells = [ int((extents[2] - extents[0]) / numpy.min(numpy.abs(numpy.diff(x)))),
                  int((extents[3] - extents[1]) / numpy.min(numpy.abs(numpy.diff(y)))) ]
    t = numpy.array([0.0,1.0])
    X, Y = numpy.meshgrid(numpy.linspace(extents[0],extents[2],num_cells[0]), 
                          numpy.linspace(extents[1],extents[3],num_cells[1]))
    Z = numpy.zeros((num_cells[1], num_cells[0], 2))
    Z[:,:,1] = interp.griddata((x, y), z, (X, Y), method='linear', fill_value=0.0)

    return t, X, Y, Z


def write_deformation_to_file(t, X, Y, Z, output_file, topo_type=1):
    r"""Write out a dtopo file to *output_file*

    input
    -----
     - *t* (numpy.ndarray[:]) - Array containing time points, note that 
       *t.shape[0] == Z.shape[2]*.
     - *X* (numpy.ndarray[:,:]) - Array containing x-coodinates (longitude), 
       should be in the form given by *numpy.meshgrid*.
     - *Y* (numpy.ndarray[:,:]) - Array containing y-coordinates (latitude),
       should be in the form given by *numpy.meshgrid*.
     - *Z* (numpy.ndarray[:,:,:]) - Array containing deformation from original
       bathymetry.
     - *output_file* (path) - Path to the output file to written to.
     - *topo_type* (int) - Type of topography file to write out.  Default is 1.

    """

    # Temporary catch for non implemented topo_type input
    if topo_type != 1:
        raise NotImplementedError("Topography types 2 and 3 are not yet supported.")

    # Construct each interpolating function and evaluate at new grid
    try:
        outfile = open(output_file, 'w')

        if topo_type == 1:
            # Topography file with 4 columns, t, x, y, dz written from the upper
            # left corner of the region
            Y_flipped = numpy.flipud(Y)
            for n in xrange(t.shape[0]):
                Z_flipped = numpy.flipud(Z[:,:,n])
                for j in xrange(Y.shape[0]):
                    for i in xrange(X.shape[1]):
                        outfile.write("%s %s %s %s\n" % (t[n], X[j,i], Y_flipped[j,i], Z_flipped[j,i]))
    
        elif topo_type == 2 or topo_type == 3:
            raise NotImplementedError("Topography types 2 and 3 are not yet supported.")
        else:
            raise ValueError("Only topography types 1, 2, and 3 are supported.")

    except IOError as e:
        raise e
    finally:
        outfile.close()


def read_dtopo_file(path, topo_type=1):
    r""""""

    if topo_type != 1:
        raise ValueError("Topography type != 1 is not implemented.")

    # Load raw data
    data = numpy.loadtxt(path)

    # Parse data
    t = data[:,0]
    x = data[:,1]
    y = data[:,2]

    # Initialize extents
    t0 = t[0]
    lower = [x[0], y[0]]
    upper = [None, None]
    num_cells = [0,0]

    # Count total x-values
    for row in xrange(1,data.shape[0]):
        if x[row] == x[0]:
            num_cells[0] = row
            break

    # Count total y-values
    for row in xrange(num_cells[0], data.shape[0]):
        if t[row] != t0:
            num_cells[1] = row / num_cells[0]
            num_times = data.shape[0] / row
            break

    # Check extents
    assert(t[0] != t[num_cells[0] * num_cells[1] + 1])
    # assert(t[0] == t[num_cells[0] * num_cells[1]])

    # Fill in rest of pertinent data
    t = data[::num_cells[0] * num_cells[1], 0]
    x = data[:num_cells[0], 1]
    y = data[:num_cells[0] * num_cells[1]:num_cells[0], 2]
    upper = [x[-1], y[-1]]
    X, Y = numpy.meshgrid(x, y)
    Z = numpy.empty( (num_times, num_cells[0], num_cells[1]) )

    for (n,time) in enumerate(t):
        Z[n,:,:] = data[num_cells[0] * num_cells[1] * n:
                        num_cells[0] * num_cells[1] * (n+1), 3].reshape(
                                (num_cells[0], num_cells[1]))

    return t, X, Y, Z



if __name__ == "__main__":

    # path = os.path.abspath("../tohoku2011-paper1/sources/Ammon.txydz")
    path = os.path.abspath("./initFig3a.dat")

    if len(sys.argv) > 1:
        path = sys.argv[1]

    extents, x, y, z = read_deformation(path)

    # Plot data
    colorbar_limits = [numpy.min(z), numpy.max(z)]
    if -colorbar_limits[0] >= colorbar_limits[1]:
        colorbar_limits[1] = -colorbar_limits[0]
    else:
        colorbar_limits[0] = -colorbar_limits[1]
    cmap = colormaps.make_colormap({1.0:'r',0.5:'w',0.0:'b'})

    # Plot original data
    fig, axes = plt.subplots(1)
    plot = axes.scatter(x, y, c=z, vmin=colorbar_limits[0],
                                   vmax=colorbar_limits[1], cmap=cmap)
    axes.set_title("Original Data")
    axes.set_aspect('equal')
    cb = fig.colorbar(plot, ax=axes)
    cb.set_label('Deformation (m)')

    # # Project and write out deformation
    t, X, Y, Z = project_deformation(extents, x, y, z)
    output_file = "./saito.xyzt"
    write_deformation_to_file(t, X, Y, Z, output_file)

    # Plot new data
    fig, axes = plt.subplots(2)
    import pdb; pdb.set_trace()
    for frame in xrange(2):
        im = axes[frame].pcolormesh(X, Y, Z[:,:,frame], vmin=colorbar_limits[0], 
                                                        vmax=colorbar_limits[1],
                                                        cmap=cmap)
        axes[frame].set_title("Projected Data")
        axes[frame].set_aspect('equal')
    cb = fig.colorbar(im, ax=axes[1])
    cb.set_label('Deformation (m)')

    plt.show()
