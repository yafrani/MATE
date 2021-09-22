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
from SeqEvolution import *
from CoEvolution import *
from GPSetup import *

import numpy as np

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

def run_target_wrapper(inst_param):
    return run_target_static(inst_param[0], inst_param[1])


# Initialise parameter values arbitrarily: use average of parameter interval
for inst in instances:
    GP.ref_param_values[inst[0]] = []
    for parameter in parameters:
        lbound = float(parameter[1]) if len(parameter)>=3 else -999999999999
        rbound = float(parameter[2]) if len(parameter)>=3 else +999999999999
        GP.ref_param_values[inst[0]].append( str((lbound+rbound)/2.0) )
#print('>>>>>>',GP.ref_param_values)


# Initialise parameter values based on best score / for each instance
mean_references = {}  # dict to store mean best parameter values
for inst in instances:
    mean_references[inst[0]] = -inf

for u in range(INIT_ITERATIONS):
    for i in range(len(parameters)):
        # Tune for parameter i
        parameter = parameters[i]

        #==========================================================
        # Generate references fitnesses for each instance
        # and select best
        #==========================================================
        
        param_name = parameter[0]  # parameter to run
        lbound = float(parameter[1]) if len(parameter)>=3 else -999999999999
        rbound = float(parameter[2]) if len(parameter)>=3 else +999999999999
        step = float(rbound-lbound)/NB_PARAM_CANDIDATES
        # calculate initial references
        print("pre-tuning", param_name+":")
        for inst in instances:
            print("instance",inst[0])
            for r in range(0, NB_PARAM_CANDIDATES):
                # generate parameter values
                param_value = lbound + step*r + step/2.0

                tmp = GP.ref_param_values[inst[0]][i]
                GP.ref_param_values[inst[0]][i] = str(param_value)

                #==============================
                # run multiple times
                scores_list = None
                #with Pool(SAMPLE_RUNS) as p:
                with Pool(1) as p:
                    scores_list = p.map(run_target_wrapper, [ [inst[0], GP.ref_param_values[inst[0]] ] ] *SAMPLE_RUNS)
                inst_score = mean(scores_list)
                max_score = max(scores_list)
                #_, pval = stats.ranksums(new_scores, current_scores)

                #print('=> MEAN:', inst_score,'| REF:',mean_references[inst[0]],'|MAX:',max_score)
                
                # if score is better, keep new parameter value and update mean value reference
                if (inst_score > mean_references[inst[0]]):
                    mean_references[inst[0]] = inst_score
                else:
                    GP.ref_param_values[inst[0]][i] = tmp

                # update score references if max current score is better
                if (max_score > GP.references[inst[0]]):
                    GP.references[inst[0]] = inst_score

        print('PARAM REFERENCES | it='+str(u)+' | p='+param_name+':')
        print(GP.ref_param_values)

        print('=============================================')
        print('Score references:')
        print('=============================================')
        for (inst, score) in GP.references.items():
            print(inst+':', score)
        print('=============================================')






#==========================================================
# GP Co-evolution
#==========================================================
pops = CoEvolution()
pops.evolution()

'''
#==========================================================
# store final populations
#==========================================================
result_pop = open("./output/result_pop-" + dt + ".txt", "w+")
for i in range(len(parameters)):

    #==========================================================
    # Tune for parameter i
    #==========================================================
    parameter = parameters[i]
    result_pop.write('Parameter: ' + parameter[0] + '\n')
    result_pop.write(str(pops.gp[i].output_csv()) + '\n')
    result_pop.write('==============================' + '\n')
    result_pop.flush()
result_pop.close()
#==========================================================
'''
