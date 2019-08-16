#!/usr/bin/python3

################################################################################
# DESC:
# Simple randomised search
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - nb_iter=size^2
# - instance-name: one-max size
# - param: mutation rate
# - python3 randsearch_mut.py 10 0.5 1
################################################################################

import sys
from random import random, randint, seed
import copy

instance = sys.argv[1]
mut_rate = float(sys.argv[2])

deb = False
if (len(sys.argv)>3 and sys.argv[3]==str(1)):
    deb = True

if (deb): print("Instance: onemax", instance)
size = int(instance)

nb_iter=size**2

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
    # flip each bit according to the mutation rate
    for j in range(0, size):
        randj = random()
        if (randj>=mut_rate): 
           if (solx[j] == 1):
              solx[j] = 0
           else :
              solx[j] = 1
    # check if the new solution is better than the current one
    fsolx = fitness(solx)
    if (fsolx>fsol1):
        sol1 = solx
        fsol1 = fsolx
    
    if (deb): print(i, sol1, fsol1)


if (deb): print('Score: ', end='')
print(fsol1, end='')
if (deb): print()
