#!/usr/bin/python3

################################################################################
# DESC:
# RLS for leading ones
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: leading one size
# - param: mutation rate
#
# EXAMPLE:
# - python3 RLS_leading.py 10 0.5 1
#
# number of iterations is set to size*log(size) # try with n^2
################################################################################

import sys
from random import random, randint, seed
from math import log, ceil
import copy

instance = sys.argv[1]
mut_rate = float(sys.argv[2])

deb = False
if (len(sys.argv)>3 and sys.argv[3]==str(1)):
    deb = True

if (deb): print("Instance: leading ones", instance)
size = int(instance)

nb_iter = ceil(size*log(size))
#nb_iter = ceil(size*size)

if (mut_rate>1 or mut_rate<0):
    print("-1")
    exit()

def fitness(sol):   
    count = 0 
    for i in range(0, size): 
        if (sol[i] == 1): 
            count+= 1  
        else: 
            break
    return count

sol1 = [randint(0, 1) for i in range(size)] # select tournament contenders
fsol1 = fitness(sol1)

if (deb): print(sol1, fsol1)

if (deb): print ("=> Start optimisation")
for i in range(1, nb_iter+1):

    # clone current solution
    solx = sol1.copy()

    # flip each bit according to the mutation rate
    for j in range(0, size):
        if (random()<=mut_rate): 
            solx[j] = 0 if solx[j] == 1 else 1

    # check if the new solution is better than the current one
    fsolx = fitness(solx)
    if (fsolx>fsol1):
        sol1 = solx
        fsol1 = fsolx
    
    if (deb): print(i, sol1, fsol1)


if (deb): print('Score: ', end='')
print(fsol1, end='')
if (deb): print()
