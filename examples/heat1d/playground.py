
from pySDC import CollocationClasses as collclass

import numpy as np
np.set_printoptions(linewidth=120)

from examples.heat1d.ProblemClass import heat1d
from examples.heat1d.TransferClass import mesh_to_mesh_1d
from pySDC.datatype_classes.mesh import mesh, rhs_imex_mesh
from pySDC.sweeper_classes.imex_1st_order import imex_1st_order
# import pySDC.PFASST_blockwise as mp
import pySDC.PFASST_stepwise as mp
# import pySDC.Methods as mp
from pySDC import Log
# from pySDC.Stats import grep_stats, sort_stats

from pySDC.Plugins.visualization_tools import show_residual_across_simulation



if __name__ == "__main__":

    # set global logger (remove this if you do not want the output at all)
    logger = Log.setup_custom_logger('root')

    num_procs = 1

    # This comes as read-in for the level class  (this is optional!)
    lparams = {}
    lparams['restol'] = 1E-10

    # This comes as read-in for the step class (this is optional!)
    sparams = {}
    sparams['maxiter'] = 20
    sparams['fine_comm'] = True

    # This comes as read-in for the problem class
    pparams = {}
    pparams['nu'] = 0.02
    # pparams['nvars'] = [127,63]
    pparams['nvars'] = 7

    # This comes as read-in for the transfer operations (this is optional!)
    tparams = {}
    tparams['finter'] = False
    tparams['iorder'] = 6
    tparams['rorder'] = 2

    # Fill description dictionary for easy hierarchy creation
    description = {}
    description['problem_class'] = heat1d
    description['problem_params'] = pparams
    description['dtype_u'] = mesh
    description['dtype_f'] = rhs_imex_mesh
    description['collocation_class'] = collclass.CollGaussRadau_Right
    description['num_nodes'] = 3
    description['sweeper_class'] = imex_1st_order
    description['level_params'] = lparams
    # description['transfer_class'] = mesh_to_mesh_1d
    # description['transfer_params'] = tparams

    # quickly generate block of steps
    MS = mp.generate_steps(num_procs,sparams,description)

    # setup parameters "in time"
    t0 = 0
    dt = 0.01
    Tend = 1*dt

    # get initial values on finest level
    P = MS[0].levels[0].prob
    uinit = P.u_exact(t0)
    print("initial: %s" % uinit)

    # call main function to get things done...
    uend,stats = mp.run_pfasst(MS,u0=uinit,t0=t0,dt=dt,Tend=Tend)

    # compute exact solution and compare
    uex = P.u_exact(Tend)
    print("exact: %s" % uex)

    print('error at time %s: %s' %(Tend,np.linalg.norm(uex.values-uend.values,np.inf)/np.linalg.norm(
        uex.values,np.inf)))


    # show_residual_across_simulation(stats,'res_vis_test.png')

    # extract_stats = grep_stats(stats,iter=-1,type='residual')
    # sortedlist_stats = sort_stats(extract_stats,sortby='step')
    # print(extract_stats,sortedlist_stats)
