#!/usr/bin/python3

################################################################################
# DESC:
# RLS for one-max
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: one-max n
# - param: mutation rate
#
# EXAMPLE:
# - python3 EA_onemax.py 10 0.5 1
#
# number of iterations is set to n*log(n)
################################################################################

import sys
from random import random, randint, seed
from math import log, ceil
import copy
from gmpy2 import popcount


instance_name = sys.argv[1].split('_')
nb_bits = int(float(sys.argv[2]))

deb = False
if (len(sys.argv)>3 and sys.argv[3]==str(1)):
    deb = True

if (deb): print("Instance: onemax", instance)
m = int(instance_name[0])
n = int(instance_name[1])

#nb_iter = ceil(2*n**m)
nb_iter = ceil(n**m)

if (nb_bits>n or nb_bits<0):
    print("-1", end='')
    exit()

#def fitness_om(sol):
#    return sol.count(1)

def fitness(sol):
    #fom = fitness_om(sol)
    fom = sol.count(1)
    if fom<=n-m or fom==n:
        return m+fom
    return n-fom

sol1 = [randint(0, 1) for i in range(n)] # select tournament contenders
fsol1 = fitness(sol1)

if (deb): print(sol1, fsol1)

if (deb): print ("=> Start optimisation")
for i in range(1, nb_iter+1):

    # clone current solution
    #solx = sol1.copy()
    #solx=[*sol1]

    # flip each bit according to the mutation rate
    idx = []
    for j in range(nb_bits):
        rnd_idx = randint(0, n-1)
        idx.append( rnd_idx )
        sol1[rnd_idx] = 0 if sol1[rnd_idx] == 1 else 1

    # check if the new solution is better than the current one
    fsolx = fitness(sol1)
    if (fsolx>fsol1):
        #sol1 = solx
        fsol1 = fsolx
    else:
        for j in range(nb_bits):
            #rnd_idx = randint(0, n-1)
            #idx.add( rnd_idx )
            sol1[ idx[j] ] = 0 if sol1[ idx[j] ] == 1 else 1

    
    if (deb): print(i, sol1, fsol1)


if (deb): print('Score: ', end='')
print(fsol1, end='')
if (deb): print()
