#!/usr/bin/python3

################################################################################
# DESC:
# Simple randomised search
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: one-max size
# - param: number of iteration
################################################################################

import sys
from random import random, randint, seed
import copy

instance = sys.argv[1]
nb_iter = int(sys.argv[2])

deb = False
if (len(sys.argv)>3 and sys.argv[3]==str(1)):
    deb = True

if (deb): print("Instance: onemax", instance)
size = int(instance)

if (nb_iter>size*size or nb_iter<1):
    print("-1")
    exit()

def fitness(sol):
    return sol.count(1)


sol1 = [randint(0, 1) for i in range(size)] # select tournament contenders
fsol1 = fitness(sol1)

if (deb): print(sol1, fsol1)

if (deb): print ("=> Start optimisation")
for i in range(1, nb_iter+1):
    # clone current solution
    solx = sol1.copy()

    randi = randint(0, size-1)
    solx[randi] = 1 if solx[randi]==0 else 0

    fsolx = fitness(solx)
    if (fsolx>fsol1):
        sol1 = solx
        fsol1 = fsolx
    
    if (deb): print(i, sol1, fsol1)


if (deb): print('Score: ', end='')
print(fsol1, end='')
if (deb): print()
