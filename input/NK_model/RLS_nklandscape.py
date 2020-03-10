# -*- coding: utf-8 -*-
'''
Created on Thu Jun 14 15:07:29 2018

@author: Maciej Workiewicz

The code has been tested on Python 2.7 and 3.6 and higher
'''
################################################################################
# DESC:
# RLS for NK-landscape
# 
# USAGE:
# python3 EA_nklandscape.py 10 2 8 1 3
#
# EXAMPLE:
# - Params:
#   - N
#   - K
#   - Neighborgood type
#   - number of landscapes
#   - number of bits
# number of iterations is set to size*log(size)
# =============================================================================

print('''
----------------------------------------------------
Running RLS 
----------------------------------------------------
''')

import numpy as np
from os.path import expanduser  # new
import matplotlib.pyplot as plt
import sys
from math import log, ceil
import os # new
from random import random, randint, seed

# Do not change these parameters--------------------------------------------
N = int(sys.argv[1])  #    set to N=6
i = int(sys.argv[4]) # number of landscapes
t = ceil(N*log(N)) #50  # time periods set to 50 initially
# --------------------------------------------------------------------------

'''
You can experiment with different setting of the following two variables:
which_imatrix - select 1 for random IM; 2 modular; 3 nearly-mod; 4 diagonal

K - set to 2 for which_imatrix = 2, 3, and 4. For which_imatrix=1 you can choose
    K from 0 (no interactions) to N-1 (maximum interactions)
'''

# You can change those ---
which_imatrix = int(sys.argv[3])      # | type of the interaction matrix
K = int(sys.argv[2])                 # | number of interdependencies per decision variable
#p_jump = float(sys.argv[5])          # | probability of a long jump in a given round
nb_bits = int(float(sys.argv[5]))          # | probability of a long jump in a given round
# ------------------------

#if which_imatrix >1:  # to avoid a common mistake
 #   K = 2

# *** 1. LOAD THE NK LANDSCAPE FILE *****************************************

#file_name = expanduser("~")
file_name = os.path.expanduser(".")  # we will save it in your home folder
NK_landscape = np.load(file_name + '/NK_workshop/NK_land_type_' + str(which_imatrix) +'_N_' + str(N) +
        '_K_' + str(K) + '_i_' + str(i) + '.npy')

power_key = np.power(2, np.arange(N - 1, -1, -1))


# *** 2. LOCAL SEARCH EA***************************************

Output2 = np.zeros((i, t))

for i1 in np.arange(i):
    combination = np.random.binomial(1, 0.5, N)  # gen initial combination
    row = np.sum(combination*power_key)  # finding the address in the array
    fitness = NK_landscape[i1, row, 2*N]  # piggyback on work done previously
    max_fit = np.max(NK_landscape[i1, :, 2*N])
    min_fit = np.min(NK_landscape[i1, :, 2*N])
    fitness_norm = (fitness - min_fit)/(max_fit - min_fit)  # normalize 0 to 1
    for t1 in np.arange(t):  # time for local search
        Output2[i1, t1] = fitness_norm
        new_combination = combination.copy()
        for j in range(nb_bits):
        	idx = randint(0, N-1) 
        	new_combination[idx] = 0 if new_combination[idx] == 1 else 1

        row = np.sum(new_combination*power_key)
        new_fitness = NK_landscape[i1, row, 2*N]
        if new_fitness > fitness:  # if we have found a better combination
            combination = new_combination.copy()
            fitness = new_fitness.copy()
            fitness_norm = (fitness - min_fit)/(max_fit - min_fit)
        # otherwise all stays the same as in the previous round
Fitness2 = np.mean(Output2, axis=0)

print('Final fitness level: ' + str(Fitness2[t-1]))

# END OF LINE
