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

instance_name = sys.argv[1].split('_')
nb_bits = int(float(sys.argv[2]))

deb = False
if (len(sys.argv)>3 and sys.argv[3]==str(1)):
    deb = True

if (deb): print("Instance: onemax", instance)
m = int(instance_name[0])
n = int(instance_name[1])

nb_iter = ceil(n*log(n))

if (nb_bits>n or nb_bits<0):
    print("-1", end='')
    exit()

def fitness_om(sol):
    return sol.count(1)
def fitness(sol):
    fom = fitness_om(sol)
    if fom<=n-m or fom==n:
        return m+fom
    return n-fom

sol1 = [randint(0, 1) for i in range(n)] # select tournament contenders
fsol1 = fitness(sol1)

if (deb): print(sol1, fsol1)

if (deb): print ("=> Start optimisation")
for i in range(1, nb_iter+1):

    # clone current solution
    solx = sol1.copy()

    # flip each bit according to the mutation rate
    for j in range(nb_bits):
        idx = randint(0, n-1)
        solx[idx] = 0 if solx[idx] == 1 else 1

    # check if the new solution is better than the current one
    fsolx = fitness(solx)
    if (fsolx>fsol1):
        sol1 = solx
        fsol1 = fsolx
    
    if (deb): print(i, sol1, fsol1)


if (deb): print('Score: ', end='')
print(fsol1, end='')
if (deb): print()
