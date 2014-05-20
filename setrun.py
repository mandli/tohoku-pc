"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

import os

import numpy

import clawpack.clawutil.data as data
import clawpack.geoclaw.surge as surge

#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    ndim = 2
    rundata = data.ClawRunData(claw_pkg, ndim)

    #------------------------------------------------------------------
    # Problem-specific parameters to be written to setprob.data:
    #------------------------------------------------------------------

    rundata.add_data(surge.data.FrictionData(),'friction_data')

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------

    rundata = setgeo(rundata)   # Defined below

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------

    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = ndim

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = 130.
    clawdata.upper[0] = 170.

    clawdata.lower[1] = 20.
    clawdata.upper[1] = 60.


    # Number of grid cells:
    clawdata.num_cells[0] = 20
    clawdata.num_cells[1] = 20


    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 4

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 2



    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # Restart from checkpoint file of a previous run?
    # Note: If restarting, you must also change the Makefile to set:
    #    RESTART = True
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False               # True to restart from prior results
    clawdata.restart_file = 'fort.chk00036'  # File to use for restart data


    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    if clawdata.output_style == 1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.num_output_times = 16
        clawdata.tfinal = 4 * 3600.
        clawdata.output_t0 = True

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = list(numpy.arange(0,3600,360)) \
                              + list(3600*numpy.arange(0,21,0.5))

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 2
        clawdata.total_steps = 6
        clawdata.output_t0 = True
        

    clawdata.output_format = 'binary'      # 'ascii' or 'netcdf' 

    clawdata.output_q_components = 'all'   # need all
    clawdata.output_aux_components = 'all'  # eta=h+B is in q
    clawdata.output_aux_onlyonce = False    # output aux arrays each frame



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 5



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.016

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.75
    clawdata.cfl_max = 1.0

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 5000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    clawdata.limiter = ['mc', 'mc', 'mc']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'godunov'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'extrap'
    clawdata.bc_upper[0] = 'extrap'

    clawdata.bc_lower[1] = 'extrap'
    clawdata.bc_upper[1] = 'extrap'


    # --------------
    # Checkpointing:
    # --------------

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif clawdata.checkpt_style == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = [0.1,0.15]

    elif clawdata.checkpt_style == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5


    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata


    # max number of refinement levels:
    amrdata.amr_levels_max = 5

    # List of refinement ratios at each level (length at least amr_levels_max-1)
    amrdata.refinement_ratios_x = [4,6,5,4]
    amrdata.refinement_ratios_y = [4,6,5,4]
    amrdata.refinement_ratios_t = [1,1,1,1]


    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','capacity','yleft','center']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    amrdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    amrdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0  

    #  ----- For developers ----- 
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = True       # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py


    # ---------------
    # Regions:
    # ---------------
    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    rundata.regiondata.regions.append([1, 3, 0., 1e9, 0, 360, -90, 90])
    rundata.regiondata.regions.append([4, 5, 0., 1000., 140,146,35,41])


    # ---------------
    # Gauges:
    # ---------------
    rundata.gaugedata.gauges = []
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    rundata.gaugedata.gauges.append([21401, 152.583, 42.617,  1800., 1.e10])   
    rundata.gaugedata.gauges.append([21413, 152.1167, 30.5153,  1800., 1.e10])   
    # rundata.gaugedata.gauges.append([21414, 178.281, 48.938,  1800., 1.e10])
    # rundata.gaugedata.gauges.append([21415, 171.849, 50.183,  1800., 1.e10])
    # rundata.gaugedata.gauges.append([21416, 163.505, 48.052,  1800., 1.e10])
    rundata.gaugedata.gauges.append([21418, 148.694, 38.711,     0., 1.e10])   
    rundata.gaugedata.gauges.append([21419, 155.736, 44.455,  1800., 1.e10])  
    # rundata.gaugedata.gauges.append([51407, 203.484, 19.642, 22000., 1.e10])
    # rundata.gaugedata.gauges.append([52402, 154.116, 11.883, 10000., 1.e10])
    rundata.gaugedata.gauges.append([1,  140.846971, 36.351141, 0.0, 1e10])
    rundata.gaugedata.gauges.append([2,  141.115000, 37.420000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([3,  141.100000, 38.160000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([4,  141.328223, 38.325000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([5,  141.510000, 38.425000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([6,  141.525000, 38.575000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([7,  141.545000, 38.660000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([8,  141.730000, 38.880000, 0.0, 1e10])
    rundata.gaugedata.gauges.append([9,  142.115489, 39.752675, 0.0, 1e10])
    rundata.gaugedata.gauges.append([10, 142.140317, 39.752675, 0.0, 1e10])
    rundata.gaugedata.gauges.append([11, 141.626825, 40.989026, 0.0, 1e10])
    rundata.gaugedata.gauges.append([12, 141.133576, 42.133955, 0.0, 1e10])
    rundata.gaugedata.gauges.append([13, 143.739806, 42.535828, 0.0, 1e10])
      
     


    # =====================
    #  Set friction values
    # =====================
    set_friction(rundata)

    return rundata
    # end of function setrun
    # ----------------------


#-------------------
def setgeo(rundata):
#-------------------
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        geo_data = rundata.geo_data
    except:
        print "*** Error, this rundata has no geodata attribute"
        raise AttributeError("Missing geodata attribute")
       
    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 2
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-3
    geo_data.friction_forcing = True
    geo_data.manning_coefficient = 0.025
    geo_data.friction_depth = 1e6

    # Refinement settings
    refinement_data = rundata.refinement_data
    refinement_data.variable_dt_refinement_ratios = True
    refinement_data.wave_tolerance = 2.e-2
    refinement_data.deep_depth = 1e2
    refinement_data.max_level_deep = 4

    # == settopo.data values ==
    topo_data = rundata.topo_data
    # for topography, append lines of the form
    #   [topotype, minlevel, maxlevel, t1, t2, fname]
    topodir = os.path.expandvars('$SRC/tohoku2011-paper1/topo')
    topo_data.topofiles.append([3, 1, 1, 0., 1.e10,
                           os.path.join(topodir,'etopo1min139E147E34N41N.asc')])
    topo_data.topofiles.append([3, 1, 1, 0., 1.e10,
                            os.path.join(topodir,'etopo4min120E72W40S60N.asc')])

    # == setdtopo.data values ==
    dtopo_data = rundata.dtopo_data
    # for moving topography, append lines of the form:  (<= 1 allowed for now!)
    #   [topotype, minlevel,maxlevel,fname]
    dtopodir = os.path.expandvars('$SRC/tohoku2011-paper1/sources/')
    dtopo_data.dtopofiles.append([1, 4, 4,
                                       os.path.join(dtopodir, 'Ammon.txydz')])
    # dtopodir = os.getcwd()
    # dtopo_data.dtopofiles.append([1, 4, 4,
    #                                    os.path.join(dtopodir, 'saito.xyzt')])


    # == setqinit.data values ==
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = []
    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [minlev, maxlev, fname]

    # == setfixedgrids.data values ==
    fixed_grids = rundata.fixed_grid_data
    # for fixed grids append lines of the form
    # [t1,t2,noutput,x1,x2,y1,y2,xpoints,ypoints,\
    #  ioutarrivaltimes,ioutsurfacemax]

    return rundata
    # end of function setgeo
    # ----------------------


def set_friction(rundata):

    data = rundata.friction_data

    # Variable friction
    data.variable_friction = False

    return data


if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    if len(sys.argv) == 2:
	rundata = setrun(sys.argv[1])
    else:
	rundata = setrun()

    rundata.write()

