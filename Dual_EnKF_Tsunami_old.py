#!/usr/bin/env python

"""
The functions below implement the Dual Ensemble Kalman filter for 
state-parameter estimation of the Tsunami model. The parameters 
characterizes the earthquake (location, intensity, ...) that happens in 
the sea. These parameters are only estimated at the initial time (t=0) 
before the Tsunami waves start. Shallow water equations are then used to 
propagate the resulting waves. 

"""

# Script originally adapted from matlab

import numpy

def swe_model(t, t_obs, fault_params=None):
    r"""Evolve the shallow water model to t_observation from t_current

    Input
    -----
     - *t* - (float) - Current time
     - *t_obs* - (float) - Observation time, will run model to this time
     - *fault_params* - (FaultData) - Data object containing fault specification,
       if `fault_params = None` then continue from current time of model,
       otherwise restart model with initial conditions using the 
       `fault_params`.  Defaults to `None`.

    Output
    ------
     - state - (ndarray) - Vector form of the state of the model at `t_obs`.
    """

    if fault_params is not None:
        # Restart
        raise NotImplemented("Restart not implemented yet.")
    else:
        # Continue to run GeoClaw forward
        pass

    return None

def dual_ensemble_Kalman_filter(num_ensembles, num_obs, obs_times, t0, tf, t_observation, Xf, Pa, H, Y, R, sigma):
    r"""

    num_ensembles = Number of ensembles used
    t0 = Initial time
    t_observation = Time of observations
    sigma = Standard error for perturbing the observations, size = [Ny x 1]


    obs_times - (list) - List of observation times
    Y - (ndarray(num_obs, len(obs_times)) - 

    #
    # In the Dual-EnKF, two parallel filters are simultaneously utilized for 
    # the parameters and the state variables. First, the parameters might be
    # propagated (here, kept unchanged) and then updated with available data of
    # the state. The updated parameters are then used to integrate the state
    # from the initial time to the current time. The data is then used again to
    # update the state variables. 
    #
    # At the initial time, t0 we assume to have an ensemble of realizations
    # for the parameters "Pa0" of size [Np x Ne] and another ensemble for the state 
    # variables "Xa0" of size [Nx x Ne]. 
    #
    # Ne : Number of ensemble members
    # Np : Number of parameters
    # Nx : Number of state variables
    # Ny : Number of available observations 
    # No : Number of observations in time  
    # Nt : Final time
    # t0 : Initial time 
    # tc : Time at current step
    # to : Time when observations become available 
    # Xa0: Analysis ensemble of state variables at t0, size = [Nx x Ne]
    # Xa : Analysis ensemble of state variables, size = [Nx x Ne]
    # Xam: Mean of the analysis state ensemble, size = [Nx x 1] 
    # Xf : Forecast ensemble of state variables, size = [Nx x Ne]
    # Xfm: Mean of the forecast state ensemble, size = [Nx x 1]
    # Pa : Analysis ensemble of parameters, size = [Np x Ne]
    # Pam: Mean of the analysis parameter ensemble, size = [Np x 1]
    # Pf : Forecast ensemble of parameters, size = [Np x Ne]
    # Pfm: Mean of the forecast parameter ensemble, size = [Np x 1]
    # H  : Observation operator (Generally consisiting of 1s and 0s), size = [Ny x Nx]
    # Y  : Observational data matrix (vectors of data from different times), size = [Ny x No] 
    # Yc : Perturbed data ensemble at the current time, size = [Ny x Ne]
    # R  : Observational error covariance matrix , size = [Ny x Ny]
    # Apf: forecast anomaly of the parameters, size = [Np x Ne] 
    # Axf: forecast anomaly of the state variables, size = [Nx x Ne]
    # Kx : Kalman gain of the state varibles, size = [Nx x Ny]
    # Kp : Kalman gain of the parameter variables, size = [Np x Ny]
    # sig: Standard error for perturbing the observations, size = [Ny x 1]
    """

    # Xa = Current state of model shape = (, num_ensembles)
    # Xf = New state of model shape = (, num_ensembles)
    # P* = Parameter vector



    Xa0 = numpy.empty((1))
    Ny = num_obs
    Y = observations
    Yc = current_observations
    H = data_obs_mask

    for t in obs_times:

        t_current = t

        # ==================
        #  Parameter Filter
        # ==================

        # 1 - Forecast (propagation) step:
        # ================================

        # keep the same ensemble (no propagation altough a random walk is possible)
        Pf = Pa

        # Integrate the ensemble members through Shallow water model from the 
        # current time t to observation time to.  
        for e in xrange(num_ensembles):
            Xf[:,e] = run_swe_model( t_current, t_observation, Xa[:,e], Pf)

        # 2 - Analysis (update) step:
        # ===========================
        # Get the mean of the forecast state ensemble 
        Xf_mean = numpy.mean(Xf)
        # Get the mean of the forecast parameter ensemble
        Pf_mean = numpy.mean(Pf)

        # Get the forecast anomaly of the state
        Axf = 1.0 / (numpy.sqrt(num_ensembles-1)) * (Xf - numpy.tile(Xf_mean, (1, num_ensembles)))  
        # Get the forecast anomaly of the parameters
        Apf = 1.0 / (numpy.sqrt(num_ensembles-1)) * (Pf - numpy.tile(Pf_mean, (1, num_ensembles)))

        # Get the Kalman gain of the parameters 
        Kp = Apf * (H * Axf).transpose() / (( H*Axf ) * ( H*Apf ).transpose() + R)

        # Get perturbed observation ensemble at the obs. time  
        Yc = Y[:,to] * numpy.ones((1,num_ensembles)) + (sigma * numpy.ones((1,num_ensembles))) * numpy.random.normal(size=(Ny,num_ensembles))

        # Update every parameter memeber with Kalman type corection 
        for e in xrange(num_ensembles):
            Pa[:,e] = Pf[:,e] + Kp * (Yc[:,e] - H * Xf[:,e])


        # ==============
        #  State Filter
        # ==============

        # 1 - Forecast (propagation) step:
        # ================================
        for e in xrange(Ne):
            # Integrate the ensemble members through Shallow water model from 
            # time 0 t0 to observation time to.  
            Xf[:,e] = run_swe_model(t0, to, Xa0[:,e], Pa[:,e])

        # While integrating from the itial time use the updated ensemble of
        # parameters (tsunami parameters at t0) obtained from the parameter
        # filter ( Pa )

        # 2 - Analysis (update) step:
        # ===========================
        Xfm = numpy.mean(Xf)

        # Get the forecast anomaly of the state
        Axf = 1.0 / numpy.sqrt(Ne - 1) * (Xf - numpy.tile(Xfm, (1,Ne)))

        # Get the Kalman gain of the parameters
        Kx = Axf * (H * Axf).transpose() / ((H * Axf) * (H * Apf).transpose() + R)

        for e in xrange(Ne):
            Xa[:,e] = Xf[:,e] + Kx * (Yc[:,e] - H * Xf[:,e])


if __name__ == "__main__":
    my_func(1,1)