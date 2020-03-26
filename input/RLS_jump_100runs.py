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
from math import log, ceil,exp
import copy


n=[10,20,50,100,200,500]
m=[2,3]
nb_run=100

def fitness_om(sol):
    return sol.count(1)
def fitness(sol, n, m):
    fom = fitness_om(sol)
    if fom<=n-m or fom==n:
        return m+fom
    return n-fom

for instance in n:
    for jump in m:
        size = int(instance)
        vec_bit=[1, 2, 3, 4, 5]
        for nb_bits in vec_bit:
            vec_iter = [ceil(size**jump), ceil(2*(size**jump))] 
            for nb_iter in vec_iter:
                for run in range(0, nb_run):
                    nb_hit=nb_iter+1
                    print("Instance: jump", str(instance), str(jump), str(nb_bits), str(nb_iter), str(run))
                    sol1 = [randint(0, 1) for i in range(size)] # select tournament contenders
                    fsol1 = fitness(sol1, instance, jump)
                    for i in range(1, nb_iter+1):

                        # clone current solution
                        solx = sol1.copy()

                        # flip each bit according to the mutation rate
                        for j in range(nb_bits):
                            idx = randint(0, size-1)
                            solx[idx] = 0 if solx[idx] == 1 else 1

                        # check if the new solution is better than the current one
                        fsolx = fitness(solx, instance, jump)
                        if (fsolx>fsol1):
                            sol1 = solx
                            fsol1 = fsolx
                        
                        if (nb_hit==nb_iter+1 and fsol1==size):
                            nb_hit=i

                    result_line = 'Jump' + ';' + str(instance)+ ';'+ str(jump)+ ';' + str(nb_iter)+ ';' + 'RLS'+ ';' + str(nb_bits)+';' + str(run) + ';' + str(fsol1)+ ';' + str(nb_hit)
                    #print (result_line)
                    # save result
                    fmet = open('output-Jump-RLS.csv', 'a')
                    fmet.write(result_line+'\n')
                    fmet.flush()
                    fmet.close()
        
