from pySDC import CollocationClasses as collclass

import numpy as np
import matplotlib.pyplot as plt

from examples.penningtrap.ProblemClass import penningtrap,penningtrap_coarse
from examples.penningtrap.TransferClass import particles_to_particles
from pySDC.datatype_classes.particles import particles, fields
from pySDC.sweeper_classes.boris_2nd_order import boris_2nd_order
from examples.penningtrap.HookClass import particles_output
import pySDC.PFASST_blockwise as mp
# import pySDC.PFASST_stepwise as mp
from pySDC import Log
from pySDC.Stats import grep_stats, sort_stats


if __name__ == "__main__":

    # set global logger (remove this if you do not want the output at all)
    logger = Log.setup_custom_logger('root')

    num_procs = 4

    # This comes as read-in for each level (this is optional!)
    lparams = {}
    lparams['restol'] = 5E-09

    # This comes as read-in for the step class (this is optional!)
    sparams = {}
    sparams['maxiter'] = 15
    sparams['fine_comm'] = True

    # This comes as read-in for the problem
    pparams = {}
    pparams['omega_E'] = 4.9
    pparams['omega_B'] = 25.0
    pparams['u0'] = np.array([[10,0,0],[100,0,100],[1],[1]])
    pparams['nparts'] = 10
    pparams['sig'] = 0.1

    # This comes as read-in for the transfer operations (this is optional!)
    tparams = {}
    tparams['finter'] = False

    # Fill description dictionary for easy hierarchy creation
    # @torbjoern: SDC and MLSDC can be activated by providing a list of 1 or 2 elements at problem_class and/or
    # num_nodes. The max. list size defines the number of levels!
    description = {}
    description['problem_class'] = [penningtrap,penningtrap_coarse]
    # description['problem_class'] = [penningtrap]
    description['problem_params'] = pparams
    description['dtype_u'] = particles
    description['dtype_f'] = fields
    description['collocation_class'] = collclass.CollGaussLegendre
    description['num_nodes'] = [5]
    description['sweeper_class'] = boris_2nd_order
    description['level_params'] = lparams
    description['transfer_class'] = particles_to_particles # this is only needed for more than 2 levels
    description['transfer_params'] = tparams
    description['hook_class'] = particles_output # this is optional

    # quickly generate block of steps
    MS = mp.generate_steps(num_procs,sparams,description)

    # setup parameters "in time"
    t0 = 0
    dt = 0.015625
    Tend = 4*dt

    # get initial values on finest level
    P = MS[0].levels[0].prob
    uinit = P.u_init()

    # call main function to get things done...
    uend,stats = mp.run_pfasst(MS,u0=uinit,t0=t0,dt=dt,Tend=Tend)

    exit()

    extract_stats = grep_stats(stats,type='etot')
    sortedlist_stats = sort_stats(extract_stats,sortby='time')

    fig = plt.figure()
    xvals = [entry[0] for entry in sortedlist_stats[10:]]
    yvals = [abs(entry[1]-sortedlist_stats[10][1])/sortedlist_stats[10][1] for entry in sortedlist_stats[10:]]
    plt.plot(xvals,yvals,'b-')

    extract_stats = grep_stats(stats,iter=-1,type='residual')
    sortedlist_stats = sort_stats(extract_stats,sortby='step')

    fig = plt.figure()
    xvals = [entry[0] for entry in sortedlist_stats[1:]]
    yvals = [entry[1] for entry in sortedlist_stats[1:]]
    plt.plot(xvals,yvals,'rx-')


    # uex = P.u_exact(Tend)
    # print(np.linalg.norm(uex.pos.values-uend.pos.values,np.inf)/np.linalg.norm(uex.pos.values,np.inf))

    plt.show()
