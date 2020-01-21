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
from GP import *
from GPSetup import *

import platform
#print(platform.system()=='Linux')

# init internal state of random number generator
seed()

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


#==========================================================
# Tune for parameter #1
#==========================================================
parameter = parameters[0]


#==========================================================
# Generate references fitnesses for each instance
# and select best
# TODO: generalise to multiple parameters (e.g. grid search)
#==========================================================
# parameter to 
param_name = parameter[0]
lbound = int(parameter[1]) if len(parameter)>=3 else -999
rbound = int(parameter[2]) if len(parameter)>=3 else +999
# calculate initial references
for inst in instances:
    for r in range(0, 10):
        norm = (rbound+lbound)/10.0
        step = (rbound-lbound)/10.0
        # run with parameter
        param_value = lbound + step*r + step/2
        inst_score = float( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )

        if (inst_score > references[inst[0]]):
            references[inst[0]] = inst_score

print('=============================================')
print('Score references:')
print('=============================================')
for (inst, score) in references.items():
    print(inst+':', score)
print('=============================================')


#==========================================================
# GP evolution
#==========================================================
gp = GP()
best_program = gp.evolution()


#==========================================================
# save best program and simplify
#==========================================================
#best_program.draw_tree("best_program", "\nbest gen: " + str(best_gen) + " | fitness: " + str(best_fitness))

fitnesses = [evaluate(ind, executable, instances) for ind in gp.population]
best_program = deepcopy(gp.population[fitnesses.index(max(fitnesses))])
exp = best_program.infix_expression()
[exec("%s = %d" % (F,2)) for F in FEATURES]
#SIZE = symbols(' '.join(FEATURES))
sexp = simplify(exp)
print('Final expression:', exp)
print('Final simplified expression:', sexp)
#==========================================================
