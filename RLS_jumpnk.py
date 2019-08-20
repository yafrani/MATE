#!/usr/bin/python3

################################################################################
# DESC:
# Simple randomised search
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: jump (n,k)
# - param: number of iteration
# - Example: jump(10,3) for param=10
# - python3 randsearch_jump.py 10 3 20 1
################################################################################

import sys
from random import random, randint, seed
import copy

instance_n = int(sys.argv[1])
instance_k = int(sys.argv[2])
nb_iter = int(sys.argv[3])

deb = False
if (len(sys.argv)>4 and sys.argv[4]==str(1)):
    deb = True

if (deb): print("Instance: jump_n"+ str(instance_n), "_k" + str(instance_k))
size = int(instance_n)

#JUMP FUNCTION
# Escaping Large Deceptive Basins of Attraction with Heavy-Tailed Mutation Operators

def fitness(sol):
    sum_sol=sol.count(1);    
    if sum_sol<= (instance_n-instance_k) or sum_sol==instance_n:
        fitness=sum_sol+instance_k;
    else:
        fitness=sum_sol-(instance_n-instance_k);    
    return fitness   


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






