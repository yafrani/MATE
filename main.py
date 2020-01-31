#!/usr/bin/env python3

#=================================================================================
# Tuning engine (based on tiny genetic programming plus, by moshe sipper)
#=================================================================================

from random import random, randint, seed
from statistics import mean
from copy import deepcopy
from IPython.display import Image, display
from graphviz import Digraph, Source 

from sympy import simplify, symbols

from utils import *
from MPGP import *
from GPSetup import *

#import platform
#print(platform.system()=='Linux')


# init internal state of random number generator
seed()


#==========================================================
# Problem description
#==========================================================
print('=============================================')
print('Parameters:')
print('=============================================')
[print(param[0], (': ['+param[1]+','+param[2]+']') if len(param)>=3 else '') for param in parameters]
print('=============================================')

print('=============================================')
print('Features:')
print('=============================================')
print(','.join(FEATURES))
print('=============================================')

print('=============================================')
print('Instances [+Features]:')
print('=============================================')
[print(inst[0]+':', inst[1:]) for inst in instances]
print('=============================================')
#==========================================================


# Initial parameter values
# Use average of parameter interval
for inst in instances:
    GP.ref_param_values[inst[0]] = []
    for parameter in parameters:
        lbound = float(parameter[1]) if len(parameter)>=3 else -999
        rbound = float(parameter[2]) if len(parameter)>=3 else +999
        GP.ref_param_values[inst[0]].append( str((lbound+rbound)/2.0) )

print('>>>>>>',GP.ref_param_values)

# Loop through all parameters (until EOF)
nb_rep = 1
for u in range(nb_rep):
    for i in range(len(parameters)):

        #==========================================================
        # Tune for parameter #1
        #==========================================================
        parameter = parameters[i]


        #==========================================================
        # Generate references fitnesses for each instance
        # and select best
        # TODO: generalise to multiple parameters (e.g. grid search)
        #==========================================================
        # parameter to tune
        nb_runs = 10.0
        param_name = parameter[0]
        lbound = int(parameter[1]) if len(parameter)>=3 else -999
        rbound = int(parameter[2]) if len(parameter)>=3 else +999
        step = (rbound-lbound)/nb_runs
        # calculate initial references
        for inst in instances:
            for r in range(0, round(nb_runs)):
                # run with parameter
                param_value = lbound + step*r + step/2.0
                #print('==',param_value)

                tmp = GP.ref_param_values[inst[0]][i]
                GP.ref_param_values[inst[0]][i] = str(param_value)
                inst_score = run_target_static(inst[0], GP.ref_param_values[inst[0]])

                # if score is better, update reference
                if (inst_score > GP.references[inst[0]]):
                    #print('YAAAY',param_value)
                    GP.references[inst[0]] = inst_score
                else:
                    GP.ref_param_values[inst[0]][i] = tmp

        print(GP.ref_param_values)

        print('=============================================')
        print('Score references:')
        print('=============================================')
        for (inst, score) in GP.references.items():
            print(inst+':', score)
        print('=============================================')
#exit()



#==========================================================
# GP evolution
#==========================================================
pops = MPGP()
pops.coevolution()


#==========================================================
# Store final population
#==========================================================
result_pop = open("./output/result_pop-" + dt + ".txt", "w+")
for i in range(len(parameters)):

    #==========================================================
    # Tune for parameter #1
    #==========================================================
    parameter = parameters[i]
    result_pop.write('Parameter: ' + parameter[0] + '\n')
    result_pop.write(str(pops.gp[i]) + '\n')
    result_pop.write('==============================' + '\n')
    result_pop.flush()
result_pop.close()
#==========================================================

