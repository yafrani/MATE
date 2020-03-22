#!/usr/bin/python3

################################################################################
# DESC:
# RLS for leading ones
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: one-max size
# - param: mutation rate
#
# EXAMPLE:
# - python3 RLS_leadingones.py 10 0.5 1
#
# number of iterations is set to size*log(size)
################################################################################

import sys
from random import random, randint, seed
from math import log, ceil
import copy

n=[10,20,50,100,200,500]
nb_run=100

def fitness(sol):   
    count = 0 
    for i in range(0, size): 
        if (sol[i] == 1): 
            count+= 1  
        else: 
            break
    return count

for instance in n:
    size = int(instance)
    vec_bit=[1, 2]
    for nb_bits in vec_bit:
        vec_iter = [ceil(0.5*(size**2)), ceil(3/4*(size**2))]  
        for nb_iter in vec_iter:
            for run in range(0, nb_run):
                nb_hit=nb_iter+1
                print("Instance: leading ones", str(instance), str(nb_bits), str(nb_iter), str(run))
                sol1 = [randint(0, 1) for i in range(size)] # select tournament contenders
                fsol1 = fitness(sol1)
                for i in range(1, nb_iter+1):

                    # clone current solution
                    solx = sol1.copy()

                    # flip each bit according to the mutation rate
                    for j in range(nb_bits):
                        idx = randint(0, size-1)
                        solx[idx] = 0 if solx[idx] == 1 else 1

                    # check if the new solution is better than the current one
                    fsolx = fitness(solx)
                    if (fsolx>fsol1):
                        sol1 = solx
                        fsol1 = fsolx
                    
                    if (nb_hit==nb_iter+1 and fsol1==size):
                        nb_hit=i

                result_line = 'LeadingOnes' + ';' + str(instance)+ ';' + str(nb_iter)+ ';' + 'RLS'+ ';' + str(nb_bits)+';' + str(run) + ';' + str(size-fsol1)+ ';' + str(nb_hit)
                #print (result_line)
                # save result
                fmet = open('output-LeadingOnes-RLS.csv', 'a')
                fmet.write(result_line+'\n')
                fmet.flush()
                fmet.close()
